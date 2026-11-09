"""
Tests for ML services.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from django.utils import timezone

from apps.ml.services import (
    AnomalyDetector,
    ErrorClusterer,
    FailureClassifier,
    FeatureEngineer,
    AnomalyDetectionService,
    ErrorClusteringService,
)
from apps.ml.models import MLModel
from apps.releases.models import Release, TestRun, TestCaseResult, ReleaseAnalysis
from apps.issues.models import ErrorEvent, IssueGroup
from apps.api_checks.models import ApiCheck, ApiCheckResult
from apps.projects.models import Project, Environment
from apps.organizations.models import Organisation
from apps.accounts.models import User


# ==================== Fixtures ====================

@pytest.fixture
def user(db):
    return User.objects.create_user(email='test@example.com', full_name='Test User', password='pass123')


@pytest.fixture
def organisation(db, user):
    org = Organisation.objects.create(name='Test Org', slug='test-org')
    org.memberships.create(user=user, role='OWNER')
    return org


@pytest.fixture
def project(db, organisation):
    return Project.objects.create(organisation=organisation, name='Test Project', slug='test-project')


@pytest.fixture
def environment(db, project):
    return Environment.objects.create(project=project, name='staging', type='staging', is_default=True)


@pytest.fixture
def release(db, project, environment):
    return Release.objects.create(
        project=project,
        environment=environment,
        version='1.0.0',
        commit_sha='a' * 40,
        branch='main',
        workflow_run_id='run_123',
        deployed_at=timezone.now(),
    )


@pytest.fixture
def test_run(db, release):
    return TestRun.objects.create(
        release=release,
        name='unit',
        status=TestRun.Status.COMPLETED,
        total_tests=100,
        passed_tests=90,
        failed_tests=5,
        skipped_tests=3,
        error_tests=2,
        total_duration=30.5,
        idempotency_key='run_123:unit',
    )


@pytest.fixture
def release_analysis(db, release):
    return ReleaseAnalysis.objects.create(
        release=release,
        status=ReleaseAnalysis.Status.YELLOW,
        policy_version='1.0',
        rule_results=[],
        new_failures=2,
        persistent_failures=3,
        fixed_failures=1,
    )


@pytest.fixture
def api_check(db, project, environment):
    return ApiCheck.objects.create(
        project=project,
        environment=environment,
        name='Health Check',
        url='https://api.example.com/health',
        method='GET',
        expected_status=200,
        timeout_seconds=10,
        interval_seconds=300,
        is_active=True,
    )


@pytest.fixture
def api_check_results(db, api_check):
    results = []
    for i in range(5):
        results.append(ApiCheckResult.objects.create(
            api_check=api_check,
            status=ApiCheckResult.Status.SUCCESS if i < 4 else ApiCheckResult.Status.FAILURE,
            status_code=200 if i < 4 else 500,
            latency_ms=50 + i * 10,
            triggered_by='scheduled',
        ))
    return results


@pytest.fixture
def issue_group(db, project):
    return IssueGroup.objects.create(
        project=project,
        fingerprint='test_fp',
        title='Test Issue Group',
        description='Test description',
    )


@pytest.fixture
def error_events(db, project, release, issue_group):
    events = []
    for i in range(10):
        events.append(ErrorEvent.objects.create(
            project=project,
            release=release,
            issue_group=issue_group,
            fingerprint=f'fp_{i % 3}',
            exception_class='AssertionError' if i % 2 == 0 else 'ValueError',
            message=f'Error message {i}',
            traceback=f'Traceback line 1\nLine 2\nLine 3',
            source=ErrorEvent.Source.TEST_FAILURE,
            source_id=f'test_{i}',
        ))
    return events


# ==================== AnomalyDetector Tests ====================

class TestAnomalyDetector:
    """Tests for AnomalyDetector."""

    def test_fit_and_predict(self):
        """Test basic fit and predict."""
        # Create synthetic data
        np.random.seed(42)
        X_normal = np.random.randn(100, 5)  # 100 normal samples
        X_anomaly = np.random.randn(5, 5) * 10 + 20  # 5 anomalous samples
        X = np.vstack([X_normal, X_anomaly])

        detector = AnomalyDetector(contamination=0.05, random_state=42)
        detector.fit(X)

        assert detector.is_fitted is True
        assert detector.model is not None

        # Predict on same data
        is_anomaly, scores = detector.predict(X)

        assert len(is_anomaly) == 105
        assert len(scores) == 105
        assert set(is_anomaly) == {-1, 1}  # -1 = anomaly, 1 = normal

        # Anomalies should have lower (more negative) scores
        anomaly_scores = scores[is_anomaly == -1]
        normal_scores = scores[is_anomaly == 1]
        assert anomaly_scores.mean() < normal_scores.mean()

    def test_save_and_load(self, tmp_path):
        """Test model persistence."""
        np.random.seed(42)
        X = np.random.randn(50, 3)

        detector = AnomalyDetector(contamination=0.1, n_estimators=10, random_state=42)
        detector.fit(X)

        # Save
        import os
        artifact_path = os.path.join(tmp_path, 'detector.pkl')
        artifact_info = detector.save(artifact_path)

        assert os.path.exists(artifact_path)
        assert artifact_info['size'] > 0

        # Load
        loaded = AnomalyDetector.load(artifact_path)
        assert loaded.is_fitted is True
        assert loaded.contamination == 0.1
        assert loaded.n_estimators == 10

        # Predictions should match
        X_test = np.random.randn(10, 3)
        orig_pred, orig_scores = detector.predict(X_test)
        loaded_pred, loaded_scores = loaded.predict(X_test)

        np.testing.assert_array_equal(orig_pred, loaded_pred)
        np.testing.assert_allclose(orig_scores, loaded_scores)


# ==================== ErrorClusterer Tests ====================

class TestErrorClusterer:
    """Tests for ErrorClusterer."""

    def test_fit_kmeans(self):
        """Test KMeans clustering."""
        from apps.ml.services import ErrorEventFeatures

        # Create error features with distinct groups
        events = [
            ErrorEventFeatures(f'1', 'p1', 'fp1', 'AssertionError', 'login failed', 'trace...', 'test'),
            ErrorEventFeatures(f'2', 'p1', 'fp2', 'AssertionError', 'login timeout', 'trace...', 'test'),
            ErrorEventFeatures(f'3', 'p1', 'fp3', 'ValueError', 'invalid input', 'trace...', 'test'),
            ErrorEventFeatures(f'4', 'p1', 'fp4', 'ValueError', 'bad config', 'trace...', 'test'),
            ErrorEventFeatures(f'5', 'p1', 'fp5', 'ConnectionError', 'db connection failed', 'trace...', 'test'),
            ErrorEventFeatures(f'6', 'p1', 'fp6', 'ConnectionError', 'network timeout', 'trace...', 'test'),
        ] * 3  # 18 samples

        clusterer = ErrorClusterer(algorithm='kmeans', n_clusters=3, random_state=42)
        clusterer.fit(events)

        assert clusterer.is_fitted is True
        assert clusterer.vectorizer is not None
        assert clusterer.clusterer is not None

        # Predict
        clusters = clusterer.predict(events)
        assert len(clusters) == len(events)
        assert set(clusters) <= {0, 1, 2}  # 3 clusters

    def test_fit_dbscan(self):
        """Test DBSCAN clustering."""
        from apps.ml.services import ErrorEventFeatures

        events = [
            ErrorEventFeatures(f'{i}', 'p1', f'fp{i}', 'AssertionError', 'msg', 'trace', 'test')
            for i in range(20)
        ]

        clusterer = ErrorClusterer(algorithm='dbscan', eps=0.5, min_samples=2, random_state=42)
        clusterer.fit(events)

        assert clusterer.is_fitted is True

        clusters = clusterer.predict(events)
        # DBSCAN labels: -1 = noise, 0, 1, 2... = clusters
        assert len(clusters) == 20

    def test_get_cluster_keywords(self):
        """Test keyword extraction for KMeans."""
        from apps.ml.services import ErrorEventFeatures

        events = [
            ErrorEventFeatures('1', 'p1', 'fp1', 'AssertionError', 'login failed', 'trace', 'test'),
            ErrorEventFeatures('2', 'p1', 'fp2', 'AssertionError', 'login timeout', 'trace', 'test'),
            ErrorEventFeatures('3', 'p1', 'fp3', 'ValueError', 'invalid input', 'trace', 'test'),
            ErrorEventFeatures('4', 'p1', 'fp4', 'ValueError', 'bad config', 'trace', 'test'),
        ] * 5

        clusterer = ErrorClusterer(algorithm='kmeans', n_clusters=2, random_state=42)
        clusterer.fit(events)

        keywords = clusterer.get_cluster_keywords(n_top=3)
        assert isinstance(keywords, dict)
        assert all(isinstance(v, list) for v in keywords.values())


# ==================== FailureClassifier Tests ====================

class TestFailureClassifier:
    """Tests for FailureClassifier."""

    def test_fit_and_predict(self):
        """Test basic classification."""
        np.random.seed(42)
        # Create synthetic features (5 features) and labels
        n_samples = 200
        X = np.random.randn(n_samples, 5)
        y = np.random.choice(
            ['network/dependency', 'timeout', 'database', 'assertion/logic', 'configuration', 'resource'],
            size=n_samples,
            p=[0.2, 0.15, 0.15, 0.25, 0.1, 0.15],  # Realistic distribution
        )

        classifier = FailureClassifier(C=1.0, max_iter=500, random_state=42)
        classifier.fit(X, y)

        assert classifier.is_fitted is True
        assert classifier.pipeline is not None

        # Predict
        preds = classifier.predict(X[:10])
        assert len(preds) == 10
        assert all(p in classifier.CATEGORIES for p in preds)

        # Predict proba
        probas = classifier.predict_proba(X[:10])
        assert probas.shape == (10, 6)  # 6 categories
        assert np.allclose(probas.sum(axis=1), 1.0)

    def test_evaluate(self):
        """Test evaluation metrics."""
        np.random.seed(42)
        n_samples = 200
        X = np.random.randn(n_samples, 5)
        y = np.random.choice(
            ['network/dependency', 'timeout', 'database', 'assertion/logic', 'configuration', 'resource'],
            size=n_samples,
        )

        classifier = FailureClassifier(random_state=42)
        classifier.fit(X, y)

        metrics = classifier.evaluate(X, y)

        assert 'macro_f1' in metrics
        assert 'accuracy' in metrics
        assert 'classification_report' in metrics
        assert 'confusion_matrix' in metrics
        assert 'categories' in metrics
        assert metrics['categories'] == classifier.CATEGORIES
        assert 0 <= metrics['macro_f1'] <= 1
        assert 0 <= metrics['accuracy'] <= 1


# ==================== FeatureEngineer Tests ====================

class TestFeatureEngineer:
    """Tests for FeatureEngineer."""

    @pytest.fixture
    def feature_engineer(self, project):
        return FeatureEngineer(project)

    def test_extract_release_features(self, feature_engineer, release, test_run, release_analysis):
        """Test release feature extraction."""
        features = feature_engineer.extract_release_features(release)

        assert features.release_id == str(release.id)
        assert features.project_id == str(feature_engineer.project.id)
        assert features.total_tests == 100
        assert features.passed_tests == 90
        assert features.failed_tests == 5
        # failure_rate = (failed + error) / total = (5+2)/100 = 0.07
        assert features.failure_rate == 0.07
        assert features.new_failures == 2
        assert features.persistent_failures == 3

    def test_extract_error_features(self, feature_engineer, error_events):
        """Test error event feature extraction."""
        event = error_events[0]
        features = feature_engineer.extract_error_features(event)

        assert features.event_id == str(event.id)
        assert features.project_id == str(feature_engineer.project.id)
        assert features.fingerprint == event.fingerprint
        assert features.exception_class == event.exception_class

    def test_prepare_release_features(self, feature_engineer, release, test_run, release_analysis):
        """Test DataFrame preparation."""
        features = feature_engineer.extract_release_features(release)
        df = feature_engineer.to_dataframe([features])
        X, feature_names = feature_engineer.prepare_release_features(df)

        assert X.shape == (1, len(feature_names))
        assert all(name in df.columns for name in feature_names)
        assert all(df[name].dtype.kind in 'ifc' for name in feature_names)  # numeric


# ==================== High-Level Service Tests ====================

class TestAnomalyDetectionService:
    """Tests for AnomalyDetectionService."""

    @pytest.fixture
    def service(self, project):
        return AnomalyDetectionService(project)

    def test_train_model_insufficient_data(self, service, project):
        """Train should fail with insufficient releases."""
        # No releases created
        with pytest.raises(ValueError, match='Insufficient releases'):
            service.train_model()


# ==================== Integration Tests ====================

class TestMLIntegration:
    """Integration tests for ML pipeline."""

    def test_full_anomaly_pipeline(self, project, environment):
        """Test complete anomaly detection pipeline with mocked data."""
        # Create multiple releases with varying characteristics
        releases = []
        for i in range(15):
            rel = Release.objects.create(
                project=project,
                environment=environment,
                version=f'1.{i}.0',
                commit_sha='a' * 40,
                branch='main',
                workflow_run_id=f'run_{i}',
                deployed_at=timezone.now() - timezone.timedelta(days=15-i),
            )
            TestRun.objects.create(
                release=rel,
                name='unit',
                status=TestRun.Status.COMPLETED,
                total_tests=100,
                passed_tests=100 - i * 2,  # Decreasing pass rate
                failed_tests=i * 2,
                total_duration=30 + i * 2,
                idempotency_key=f'run_{i}:unit',
            )
            ReleaseAnalysis.objects.create(
                release=rel,
                status=ReleaseAnalysis.Status.GREEN if i < 5 else ReleaseAnalysis.Status.YELLOW,
                new_failures=i // 3,
                persistent_failures=i // 5,
            )
            releases.append(rel)

        service = AnomalyDetectionService(project)

        # Train model
        model = service.train_model(version='1.0.0')
        assert model is not None
        assert model.status == MLModel.Status.ACTIVE
        assert model.training_samples >= 10

        # Detect anomaly on a new release
        new_release = Release.objects.create(
            project=project,
            environment=environment,
            version='2.0.0',
            commit_sha='b' * 40,
            branch='main',
            workflow_run_id='run_new',
            deployed_at=timezone.now(),
        )
        TestRun.objects.create(
            release=new_release,
            name='unit',
            status=TestRun.Status.COMPLETED,
            total_tests=100,
            passed_tests=50,  # Big drop!
            failed_tests=50,
            total_duration=100,
            idempotency_key='run_new:unit',
        )

        result = service.detect_anomaly(new_release)
        assert result is not None
        assert 'is_anomaly' in result
        assert 'anomaly_score' in result


# Run with: pytest apps/ml/tests/test_services.py -v