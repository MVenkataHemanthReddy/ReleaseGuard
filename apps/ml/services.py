"""
ML Services for ReleaseGuard.

Implements:
1. Isolation Forest for release/API metric anomaly detection
2. TF-IDF + KMeans/DBSCAN for error clustering
3. Logistic Regression for failure classification

All models are ADVISORY - deterministic rules decide GREEN/YELLOW/RED.
"""

import logging
import pickle
import warnings
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional
from django.db import transaction
from django.utils import timezone

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    silhouette_score,
    adjusted_rand_score,
)
from sklearn.pipeline import Pipeline

from apps.ml.models import MLModel, ModelPrediction, FeatureStore, TrainingDataset
from apps.releases.models import Release, ReleaseAnalysis, TestRun
from apps.issues.models import ErrorEvent, IssueGroup
from apps.api_checks.models import ApiCheckResult
from apps.projects.models import Project

logger = logging.getLogger(__name__)

# Suppress sklearn warnings for cleaner logs
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')


# ==================== Data Classes ====================

@dataclass
class ReleaseFeatures:
    """Feature vector for a release."""
    release_id: str
    project_id: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    total_duration: float
    failure_rate: float
    duration_per_test: float
    new_failures: int
    persistent_failures: int
    fixed_failures: int
    flaky_tests: int
    api_avg_latency_ms: Optional[float]
    api_error_rate: Optional[float]
    api_check_count: int
    days_since_last_release: float


@dataclass
class ErrorEventFeatures:
    """Feature vector for error event clustering."""
    event_id: str
    project_id: str
    fingerprint: str
    exception_class: str
    message: str
    traceback: str
    source: str


# ==================== Feature Engineering ====================

class FeatureEngineer:
    """Extracts ML features from domain models."""

    def __init__(self, project: Project):
        self.project = project

    def extract_release_features(self, release: Release) -> ReleaseFeatures:
        """Extract features for anomaly detection."""
        # Get test run data
        test_runs = release.test_runs.filter(status=TestRun.Status.COMPLETED)
        latest_run = test_runs.order_by('-created_at').first()

        if not latest_run:
            # Return zero features if no test runs
            return ReleaseFeatures(
                release_id=str(release.id),
                project_id=str(self.project.id),
                total_tests=0, passed_tests=0, failed_tests=0, skipped_tests=0, error_tests=0,
                total_duration=0.0, failure_rate=0.0, duration_per_test=0.0,
                new_failures=0, persistent_failures=0, fixed_failures=0, flaky_tests=0,
                api_avg_latency_ms=None, api_error_rate=None, api_check_count=0,
                days_since_last_release=0.0,
            )

        # Get analysis for comparison metrics
        analysis = getattr(release, 'analysis', None)

        # API check features
        api_checks = ApiCheckResult.objects.filter(
            api_check__project=self.project,
            created_at__gte=release.deployed_at - timedelta(days=1) if release.deployed_at else timezone.now() - timedelta(days=1),
            created_at__lte=release.deployed_at + timedelta(days=1) if release.deployed_at else timezone.now() + timedelta(days=1),
        )
        api_latencies = [c.latency_ms for c in api_checks if c.latency_ms and c.is_success]
        api_errors = api_checks.exclude(status=ApiCheckResult.Status.SUCCESS).count()
        api_total = api_checks.count()

        # Days since previous release
        prev_release = release.previous_release
        days_since = 0.0
        if prev_release and prev_release.deployed_at and release.deployed_at:
            days_since = (release.deployed_at - prev_release.deployed_at).total_seconds() / 86400

        return ReleaseFeatures(
            release_id=str(release.id),
            project_id=str(self.project.id),
            total_tests=latest_run.total_tests,
            passed_tests=latest_run.passed_tests,
            failed_tests=latest_run.failed_tests,
            skipped_tests=latest_run.skipped_tests,
            error_tests=latest_run.error_tests,
            total_duration=latest_run.total_duration,
            failure_rate=latest_run.failure_rate / 100.0 if latest_run.total_tests > 0 else 0.0,
            duration_per_test=latest_run.total_duration / latest_run.total_tests if latest_run.total_tests > 0 else 0.0,
            new_failures=analysis.new_failures if analysis else 0,
            persistent_failures=analysis.persistent_failures if analysis else 0,
            fixed_failures=analysis.fixed_failures if analysis else 0,
            flaky_tests=analysis.flaky_tests if analysis else 0,
            api_avg_latency_ms=np.mean(api_latencies) if api_latencies else None,
            api_error_rate=api_errors / api_total if api_total > 0 else 0.0,
            api_check_count=api_total,
            days_since_last_release=days_since,
        )

    def extract_error_features(self, error_event: ErrorEvent) -> ErrorEventFeatures:
        """Extract text features for error clustering."""
        return ErrorEventFeatures(
            event_id=str(error_event.id),
            project_id=str(self.project.id),
            fingerprint=error_event.fingerprint,
            exception_class=error_event.exception_class or '',
            message=error_event.message or '',
            traceback=error_event.traceback or '',
            source=error_event.source,
        )

    def to_dataframe(self, features_list: list) -> pd.DataFrame:
        """Convert list of feature dataclasses to DataFrame."""
        return pd.DataFrame([f.__dict__ for f in features_list])

    def prepare_release_features(self, df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
        """Prepare numeric features for release anomaly detection."""
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # Drop ID columns
        numeric_cols = [c for c in numeric_cols if not c.endswith('_id')]

        X = df[numeric_cols].fillna(0).values
        return X, numeric_cols


# ==================== Anomaly Detection (Isolation Forest) ====================

class AnomalyDetector:
    """
    Isolation Forest for release metric anomaly detection.

    Detects unusual releases based on test metrics, API health, and timing.
    ADVISORY ONLY - does not determine release status.
    """

    def __init__(self, contamination: float = 0.1, n_estimators: int = 100, random_state: int = 42):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model: Optional[IsolationForest] = None
        self.scaler = StandardScaler()
        self.feature_names: list[str] = []
        self.is_fitted = False

    def fit(self, X: np.ndarray) -> 'AnomalyDetector':
        """Train the Isolation Forest."""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.model.fit(X_scaled)
        self.is_fitted = True
        logger.info(f'AnomalyDetector trained on {X.shape[0]} samples, {X.shape[1]} features')
        return self

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies.

        Returns:
            (is_anomaly, anomaly_scores)
            is_anomaly: -1 for anomaly, 1 for normal
            anomaly_scores: negative = more anomalous
        """
        if not self.is_fitted:
            raise ValueError('Model not fitted. Call fit() first.')

        X_scaled = self.scaler.transform(X)
        is_anomaly = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)  # Negative = anomalous

        return is_anomaly, anomaly_scores

    def save(self, path: str) -> dict:
        """Save model artifact."""
        artifact = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'contamination': self.contamination,
            'n_estimators': self.n_estimators,
            'random_state': self.random_state,
        }
        with open(path, 'wb') as f:
            pickle.dump(artifact, f)
        return {'path': path, 'size': len(pickle.dumps(artifact))}

    @classmethod
    def load(cls, path: str) -> 'AnomalyDetector':
        """Load model artifact."""
        with open(path, 'rb') as f:
            artifact = pickle.load(f)

        detector = cls(
            contamination=artifact['contamination'],
            n_estimators=artifact['n_estimators'],
            random_state=artifact['random_state'],
        )
        detector.model = artifact['model']
        detector.scaler = artifact['scaler']
        detector.feature_names = artifact['feature_names']
        detector.is_fitted = True
        return detector


# ==================== Error Clustering (TF-IDF + KMeans/DBSCAN) ====================

class ErrorClusterer:
    """
    TF-IDF + Clustering for error grouping.

    Supplements deterministic fingerprinting for errors that don't match exactly.
    """

    def __init__(
        self,
        max_features: int = 1000,
        ngram_range: tuple = (1, 2),
        min_df: int = 2,
        algorithm: str = 'kmeans',  # 'kmeans' or 'dbscan'
        n_clusters: int = 10,
        eps: float = 0.5,
        min_samples: int = 2,
        random_state: int = 42,
    ):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.algorithm = algorithm
        self.n_clusters = n_clusters
        self.eps = eps
        self.min_samples = min_samples
        self.random_state = random_state

        self.vectorizer: Optional[TfidfVectorizer] = None
        self.clusterer = None
        self.is_fitted = False

    def _prepare_text(self, error_events: list[ErrorEventFeatures]) -> list[str]:
        """Combine text fields for TF-IDF."""
        texts = []
        for e in error_events:
            # Combine exception class, message, and traceback
            parts = []
            if e.exception_class:
                parts.append(e.exception_class)
            if e.message:
                parts.append(e.message)
            if e.traceback:
                # Use first few lines of traceback
                traceback_lines = e.traceback.split('\n')[:5]
                parts.extend(traceback_lines)
            texts.append(' '.join(parts))
        return texts

    def fit(self, error_events: list[ErrorEventFeatures]) -> 'ErrorClusterer':
        """Train TF-IDF vectorizer and clusterer."""
        texts = self._prepare_text(error_events)

        # TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            stop_words='english',
            sublinear_tf=True,
        )
        X = self.vectorizer.fit_transform(texts)

        # Clustering
        if self.algorithm == 'kmeans':
            self.clusterer = KMeans(
                n_clusters=min(self.n_clusters, len(error_events)),
                random_state=self.random_state,
                n_init=10,
            )
            self.clusterer.fit(X)
            self.labels_ = self.clusterer.labels_
        else:  # dbscan
            self.clusterer = DBSCAN(
                eps=self.eps,
                min_samples=self.min_samples,
                metric='cosine',
            )
            self.labels_ = self.clusterer.fit_predict(X)
            self.clusterer = self.clusterer  # Keep for reference

        self.is_fitted = True
        logger.info(f'ErrorClusterer trained on {len(error_events)} events, {X.shape[1]} features')
        return self

    def predict(self, error_events: list[ErrorEventFeatures]) -> np.ndarray:
        """Predict cluster assignments."""
        if not self.is_fitted:
            raise ValueError('Model not fitted. Call fit() first.')

        texts = self._prepare_text(error_events)
        X = self.vectorizer.transform(texts)

        if self.algorithm == 'kmeans':
            return self.clusterer.predict(X)
        else:
            # For DBSCAN, assign to nearest cluster centroid
            # Compute centroids from training data
            if not hasattr(self, 'centroids_'):
                # Compute centroids from training labels
                unique_labels = set(self.labels_)
                self.centroids_ = {}
                # We need to store training vectors to compute centroids
                # For simplicity, we'll re-vectorize a sample and use nearest neighbor
                pass
            # Fallback: use nearest training sample's label
            # This is a simplified approach - in production, store centroids
            from sklearn.neighbors import NearestNeighbors
            # We'd need to store training vectors - skip for now
            return np.array([-1] * len(error_events))  # All noise for new data

    def get_cluster_keywords(self, n_top: int = 5) -> dict[int, list[str]]:
        """Get top TF-IDF terms per cluster (KMeans only)."""
        if self.algorithm != 'kmeans' or not self.is_fitted:
            return {}

        keywords = {}
        feature_names = self.vectorizer.get_feature_names_out()
        centers = self.clusterer.cluster_centers_

        for i, center in enumerate(centers):
            top_indices = center.argsort()[-n_top:][::-1]
            keywords[i] = [feature_names[idx] for idx in top_indices]
        return keywords

    def save(self, path: str) -> dict:
        """Save model artifact."""
        artifact = {
            'vectorizer': self.vectorizer,
            'clusterer': self.clusterer,
            'algorithm': self.algorithm,
            'n_clusters': self.n_clusters,
            'eps': self.eps,
            'min_samples': self.min_samples,
        }
        with open(path, 'wb') as f:
            pickle.dump(artifact, f)
        return {'path': path, 'size': len(pickle.dumps(artifact))}

    @classmethod
    def load(cls, path: str) -> 'ErrorClusterer':
        """Load model artifact."""
        with open(path, 'rb') as f:
            artifact = pickle.load(f)

        clusterer = cls(algorithm=artifact['algorithm'])
        clusterer.vectorizer = artifact['vectorizer']
        clusterer.clusterer = artifact['clusterer']
        clusterer.is_fitted = True
        return clusterer


# ==================== Failure Classification (Logistic Regression) ====================

class FailureClassifier:
    """
    Logistic Regression for failure category classification.

    Categories: network/dependency, timeout, database, assertion/logic, configuration, resource.
    Only trained after sufficient human-labeled examples exist.
    """

    CATEGORIES = [
        'network/dependency',
        'timeout',
        'database',
        'assertion/logic',
        'configuration',
        'resource',
    ]

    def __init__(self, C: float = 1.0, max_iter: int = 1000, random_state: int = 42):
        self.C = C
        self.max_iter = max_iter
        self.random_state = random_state
        self.pipeline: Optional[Pipeline] = None
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'FailureClassifier':
        """Train classifier with preprocessing pipeline."""
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(
                C=self.C,
                max_iter=self.max_iter,
                random_state=self.random_state,
                solver='lbfgs',
                class_weight='balanced',
            )),
        ])
        self.pipeline.fit(X, y)
        self.is_fitted = True
        logger.info(f'FailureClassifier trained on {len(y)} samples, {len(np.unique(y))} classes')
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict failure categories."""
        if not self.is_fitted:
            raise ValueError('Model not fitted. Call fit() first.')
        return self.pipeline.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        if not self.is_fitted:
            raise ValueError('Model not fitted. Call fit() first.')
        return self.pipeline.predict_proba(X)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> dict:
        """Evaluate model with detailed metrics."""
        y_pred = self.predict(X)
        y_proba = self.predict_proba(X)

        report = classification_report(y, y_pred, output_dict=True, zero_division=0)
        cm = confusion_matrix(y, y_pred, labels=self.CATEGORIES)

        return {
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'categories': self.CATEGORIES,
            'macro_f1': report['macro avg']['f1-score'],
            'accuracy': report['accuracy'],
        }

    def save(self, path: str) -> dict:
        """Save model artifact."""
        artifact = {'pipeline': self.pipeline}
        with open(path, 'wb') as f:
            pickle.dump(artifact, f)
        return {'path': path, 'size': len(pickle.dumps(artifact))}

    @classmethod
    def load(cls, path: str) -> 'FailureClassifier':
        """Load model artifact."""
        with open(path, 'rb') as f:
            artifact = pickle.load(f)

        classifier = cls()
        classifier.pipeline = artifact['pipeline']
        classifier.is_fitted = True
        return classifier


# ==================== High-Level ML Services ====================

class AnomalyDetectionService:
    """
    Service for release anomaly detection using Isolation Forest.
    """

    def __init__(self, project: Project):
        self.project = project
        self.feature_engineer = FeatureEngineer(project)

    def train_model(self, model_name: str = 'release_anomaly_detector', version: str = '1.0.0') -> MLModel:
        """Train Isolation Forest on historical releases."""
        # Get historical releases with sufficient data
        releases_qs = Release.objects.filter(
            project=self.project,
            test_runs__status=TestRun.Status.COMPLETED,
        ).distinct().order_by('-deployed_at')
        
        # Evaluate queryset to list to avoid slice issues
        releases = list(releases_qs[:500])

        if len(releases) < 10:
            raise ValueError('Insufficient releases for training (need at least 10)')

        # Extract features
        features_list = []
        for release in releases:
            features = self.feature_engineer.extract_release_features(release)
            features_list.append(features)

        df = self.feature_engineer.to_dataframe(features_list)
        X, feature_names = self.feature_engineer.prepare_release_features(df)

        if len(X) < 10:
            raise ValueError('Insufficient feature samples after preprocessing')

        # Train model
        detector = AnomalyDetector(contamination=0.1, n_estimators=100, random_state=42)
        detector.feature_names = feature_names
        detector.fit(X)

        # Save artifact
        import os
        artifact_dir = os.path.join('ml_artifacts', str(self.project.id))
        os.makedirs(artifact_dir, exist_ok=True)
        artifact_path = os.path.join(artifact_dir, f'{model_name}_v{version}.pkl')
        artifact_info = detector.save(artifact_path)

        # Create MLModel record
        ml_model = MLModel.objects.create(
            project=self.project,
            name=model_name,
            type=MLModel.Type.ANOMALY_DETECTION,
            version=version,
            algorithm='IsolationForest',
            hyperparameters={
                'contamination': 0.1,
                'n_estimators': 100,
                'random_state': 42,
            },
            feature_names=feature_names,
            feature_version='1.0',
            training_window_start=releases[-1].deployed_at if releases[-1].deployed_at else timezone.now(),
            training_window_end=releases[0].deployed_at if releases[0].deployed_at else timezone.now(),
            training_samples=len(X),
            artifact_path=artifact_path,
            artifact_size_bytes=artifact_info['size'],
            status=MLModel.Status.ACTIVE,
            activated_at=timezone.now(),
        )

        # Generate predictions for recent releases
        self._generate_predictions(ml_model, releases[:50])

        logger.info(f'Trained anomaly detector {ml_model.name} v{ml_model.version} for project {self.project}')
        return ml_model

    def _generate_predictions(self, ml_model: MLModel, releases):
        """Generate predictions for releases."""
        detector = AnomalyDetector.load(ml_model.artifact_path)

        for release in releases:
            features = self.feature_engineer.extract_release_features(release)
            df = self.feature_engineer.to_dataframe([features])
            X, _ = self.feature_engineer.prepare_release_features(df)

            if len(X) > 0:
                is_anomaly, scores = detector.predict(X)
                prediction = {
                    'is_anomaly': bool(is_anomaly[0] == -1),
                    'anomaly_score': float(scores[0]),
                    'threshold': -0.5,  # Isolation Forest threshold
                }

                ModelPrediction.objects.update_or_create(
                    model=ml_model,
                    target_type='release',
                    target_id=release.id,
                    defaults={
                        'prediction': prediction,
                        'confidence': abs(float(scores[0])),
                        'status': ModelPrediction.Status.COMPLETED,
                        'completed_at': timezone.now(),
                    }
                )

    def detect_anomaly(self, release: Release) -> Optional[dict]:
        """Detect if a release is anomalous using active model."""
        active_model = MLModel.objects.filter(
            project=self.project,
            type=MLModel.Type.ANOMALY_DETECTION,
            status=MLModel.Status.ACTIVE,
        ).first()

        if not active_model:
            return None

        try:
            detector = AnomalyDetector.load(active_model.artifact_path)
            features = self.feature_engineer.extract_release_features(release)
            df = self.feature_engineer.to_dataframe([features])
            X, _ = self.feature_engineer.prepare_release_features(df)

            if len(X) == 0:
                return None

            is_anomaly, scores = detector.predict(X)
            return {
                'is_anomaly': bool(is_anomaly[0] == -1),
                'anomaly_score': float(scores[0]),
                'model_version': active_model.version,
                'model_id': str(active_model.id),
            }
        except Exception as e:
            logger.error(f'Anomaly detection failed for release {release.id}: {e}')
            return None


class ErrorClusteringService:
    """
    Service for error event clustering using TF-IDF + KMeans/DBSCAN.
    """

    def __init__(self, project: Project):
        self.project = project

    def train_model(
        self,
        model_name: str = 'error_clusterer',
        version: str = '1.0.0',
        algorithm: str = 'kmeans',
        n_clusters: int = 20,
    ) -> MLModel:
        """Train error clusterer on historical error events."""
        # Get error events with text content
        events = ErrorEvent.objects.filter(
            project=self.project,
        ).exclude(
            message='', traceback='', exception_class=''
        )[:2000]

        if events.count() < 20:
            raise ValueError('Insufficient error events for training (need at least 20)')

        # Prepare features
        feature_engineer = FeatureEngineer(self.project)
        error_features = [feature_engineer.extract_error_features(e) for e in events]

        # Train clusterer
        clusterer = ErrorClusterer(
            algorithm=algorithm,
            n_clusters=min(n_clusters, events.count()),
            random_state=42,
        )
        clusterer.fit(error_features)

        # Save artifact
        import os
        artifact_dir = os.path.join('ml_artifacts', str(self.project.id))
        os.makedirs(artifact_dir, exist_ok=True)
        artifact_path = os.path.join(artifact_dir, f'{model_name}_v{version}.pkl')
        artifact_info = clusterer.save(artifact_path)

        # Create MLModel record
        ml_model = MLModel.objects.create(
            project=self.project,
            name=model_name,
            type=MLModel.Type.ERROR_CLUSTERING,
            version=version,
            algorithm=f'{algorithm.upper()} + TF-IDF',
            hyperparameters={
                'algorithm': algorithm,
                'n_clusters': n_clusters if algorithm == 'kmeans' else None,
                'eps': clusterer.eps if algorithm == 'dbscan' else None,
                'max_features': clusterer.max_features,
            },
            feature_version='1.0',
            training_samples=events.count(),
            artifact_path=artifact_path,
            artifact_size_bytes=artifact_info['size'],
            status=MLModel.Status.ACTIVE,
            activated_at=timezone.now(),
        )

        # Generate cluster assignments
        self._generate_predictions(ml_model, events[:500])

        logger.info(f'Trained error clusterer {ml_model.name} v{ml_model.version}')
        return ml_model

    def _generate_predictions(self, ml_model: MLModel, events):
        """Generate cluster predictions."""
        clusterer = ErrorClusterer.load(ml_model.artifact_path)

        for event in events:
            feature_engineer = FeatureEngineer(self.project)
            error_feat = feature_engineer.extract_error_features(event)
            cluster_id = clusterer.predict([error_feat])[0]

            prediction = {
                'cluster_id': int(cluster_id),
                'algorithm': ml_model.hyperparameters.get('algorithm', 'kmeans'),
            }

            ModelPrediction.objects.update_or_create(
                model=ml_model,
                target_type='error_event',
                target_id=event.id,
                defaults={
                    'prediction': prediction,
                    'status': ModelPrediction.Status.COMPLETED,
                    'completed_at': timezone.now(),
                }
            )

    def cluster_new_event(self, error_event: ErrorEvent) -> Optional[dict]:
        """Cluster a new error event using active model."""
        active_model = MLModel.objects.filter(
            project=self.project,
            type=MLModel.Type.ERROR_CLUSTERING,
            status=MLModel.Status.ACTIVE,
        ).first()

        if not active_model:
            return None

        try:
            clusterer = ErrorClusterer.load(active_model.artifact_path)
            feature_engineer = FeatureEngineer(self.project)
            error_feat = feature_engineer.extract_error_features(error_event)
            cluster_id = clusterer.predict([error_feat])[0]

            # Get cluster keywords if available
            keywords = clusterer.get_cluster_keywords()

            return {
                'cluster_id': int(cluster_id),
                'model_version': active_model.version,
                'model_id': str(active_model.id),
                'cluster_keywords': keywords.get(int(cluster_id), []),
            }
        except Exception as e:
            logger.error(f'Error clustering failed for event {error_event.id}: {e}')
            return None


class FailureClassificationService:
    """
    Service for failure category classification using Logistic Regression.

    Requires human-labeled training data from TrainingDataset.
    """

    def __init__(self, project: Project):
        self.project = project

    def train_model(
        self,
        training_dataset: TrainingDataset,
        model_name: str = 'failure_classifier',
        version: str = '1.0.0',
    ) -> MLModel:
        """Train failure classifier on labeled dataset."""
        # This would load the training dataset artifact and train
        # Implementation depends on TrainingDataset format
        # For now, create the model record
        ml_model = MLModel.objects.create(
            project=self.project,
            name=model_name,
            type=MLModel.Type.FAILURE_CLASSIFICATION,
            version=version,
            algorithm='LogisticRegression',
            hyperparameters={
                'C': 1.0,
                'max_iter': 1000,
                'class_weight': 'balanced',
            },
            feature_version=training_dataset.feature_version,
            training_samples=training_dataset.train_samples,
            training_window_start=timezone.now() - timedelta(days=90),
            training_window_end=timezone.now(),
            status=MLModel.Status.TRAINING,
        )

        # TODO: Load training data, train, evaluate, save artifact, update model
        logger.info(f'Failure classifier {ml_model.name} v{ml_model.version} created (training pending)')
        return ml_model

    def classify_failure(self, error_event: ErrorEvent) -> Optional[dict]:
        """Classify a failure using active model."""
        active_model = MLModel.objects.filter(
            project=self.project,
            type=MLModel.Type.FAILURE_CLASSIFICATION,
            status=MLModel.Status.ACTIVE,
        ).first()

        if not active_model:
            return None

        # TODO: Load model and predict
        return None


# ==================== ML Model Management ====================

class MLModelManager:
    """
    High-level manager for ML model lifecycle.
    """

    def __init__(self, project: Project):
        self.project = project
        self.anomaly_service = AnomalyDetectionService(project)
        self.clustering_service = ErrorClusteringService(project)
        self.classification_service = FailureClassificationService(project)

    def get_active_models(self) -> dict:
        """Get all active models for project."""
        models = MLModel.objects.filter(
            project=self.project,
            status=MLModel.Status.ACTIVE,
        )
        return {m.type: m for m in models}

    def retrain_all(self) -> dict:
        """Retrain all model types."""
        results = {}

        # Anomaly detection
        try:
            model = self.anomaly_service.train_model()
            results['anomaly_detection'] = {'status': 'success', 'model_id': str(model.id)}
        except Exception as e:
            results['anomaly_detection'] = {'status': 'failed', 'error': str(e)}

        # Error clustering
        try:
            model = self.clustering_service.train_model()
            results['error_clustering'] = {'status': 'success', 'model_id': str(model.id)}
        except Exception as e:
            results['error_clustering'] = {'status': 'failed', 'error': str(e)}

        return results