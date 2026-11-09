"""
Business logic services for ReleaseGuard releases.

Contains release comparison, deterministic policy engine, and analysis generation.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from django.db import transaction
from django.utils import timezone

from apps.releases.models import Release, TestRun, TestCaseResult, ReleaseAnalysis
from apps.releases.parsers import parse_junit_xml, generate_test_fingerprint

logger = logging.getLogger(__name__)


@dataclass
class ComparisonResult:
    """Result of comparing two releases' test results."""
    new_failures: list[TestCaseResult]
    persistent_failures: list[TestCaseResult]
    fixed_failures: list[TestCaseResult]
    unchanged_passing: list[TestCaseResult]


@dataclass
class PolicyRuleResult:
    """Result of evaluating a single policy rule."""
    rule: str
    passed: bool
    message: str
    details: dict = None
    warning: bool = False


class ReleaseComparisonService:
    """
    Compare test results between two releases.

    Identifies:
    - New failures (failed in current, passed/absent in previous)
    - Persistent failures (failed in both)
    - Fixed failures (failed in previous, passed in current)
    - Unchanged passing (passed in both)
    """

    def __init__(self, current_release: Release, previous_release: Optional[Release] = None):
        self.current_release = current_release
        self.previous_release = previous_release or current_release.previous_release

    def compare(self) -> ComparisonResult:
        """Perform comparison and return categorized results."""
        if not self.previous_release:
            logger.info('No previous release to compare for %s', self.current_release)
            return ComparisonResult(
                new_failures=list(self.current_release.test_runs.first().test_cases.filter(
                    status__in=[TestCaseResult.Status.FAILED, TestCaseResult.Status.ERROR]
                )) if self.current_release.test_runs.exists() else [],
                persistent_failures=[],
                fixed_failures=[],
                unchanged_passing=list(self.current_release.test_runs.first().test_cases.filter(
                    status=TestCaseResult.Status.PASSED
                )) if self.current_release.test_runs.exists() else [],
            )

        current_results = self._get_latest_test_results(self.current_release)
        previous_results = self._get_latest_test_results(self.previous_release)

        # Build lookup by test identifier
        current_map = {r.test_identifier: r for r in current_results}
        previous_map = {r.test_identifier: r for r in previous_results}

        all_identifiers = set(current_map.keys()) | set(previous_map.keys())

        new_failures = []
        persistent_failures = []
        fixed_failures = []
        unchanged_passing = []

        for identifier in all_identifiers:
            current = current_map.get(identifier)
            previous = previous_map.get(identifier)

            current_failed = current and current.is_failure
            previous_failed = previous and previous.is_failure
            current_passed = current and current.is_passed
            previous_passed = previous and previous.is_passed

            if current_failed and not previous_failed:
                # New failure (or new test that fails)
                new_failures.append(current)
            elif current_failed and previous_failed:
                # Persistent failure
                persistent_failures.append(current)
            elif not current_failed and previous_failed and current_passed:
                # Fixed failure
                fixed_failures.append(previous)  # Store previous to show what was fixed
            elif current_passed and previous_passed:
                # Unchanged passing
                unchanged_passing.append(current)

        return ComparisonResult(
            new_failures=new_failures,
            persistent_failures=persistent_failures,
            fixed_failures=fixed_failures,
            unchanged_passing=unchanged_passing,
        )

    def _get_latest_test_results(self, release: Release) -> list[TestCaseResult]:
        """Get latest test case results for a release (from most recent test run)."""
        latest_run = release.test_runs.filter(status=TestRun.Status.COMPLETED).order_by('-created_at').first()
        if not latest_run:
            return []
        return list(latest_run.test_cases.all())


class PolicyEngine:
    """
    Deterministic release policy evaluation engine.

    Evaluates rules in order and produces GREEN/YELLOW/RED with explanations.
    Rules are configurable via policy_version and rule definitions.
    """

    # Default policy rules (version 1.0)
    DEFAULT_RULES = [
        {
            'id': 'required_tests_pass',
            'name': 'Required Tests Pass',
            'description': 'All required tests must pass',
            'severity': 'blocking',  # blocking -> RED if failed
        },
        {
            'id': 'no_new_failures',
            'name': 'No New Failures',
            'description': 'No new test failures compared to previous release',
            'severity': 'blocking',
        },
        {
            'id': 'critical_health_checks',
            'name': 'Critical Health Checks',
            'description': 'All critical API health checks must pass',
            'severity': 'blocking',
        },
        {
            'id': 'no_persistent_failures',
            'name': 'No Persistent Failures',
            'description': 'No tests failing persistently across releases',
            'severity': 'warning',  # warning -> YELLOW if failed
        },
        {
            'id': 'flaky_test_threshold',
            'name': 'Flaky Test Threshold',
            'description': 'Flaky test rate below threshold',
            'severity': 'warning',
            'threshold': 0.05,  # 5%
        },
        {
            'id': 'test_duration_anomaly',
            'name': 'Test Duration Anomaly',
            'description': 'Total test duration within expected range',
            'severity': 'warning',
        },
    ]

    def __init__(self, release: Release, policy_version: str = '1.0', custom_rules: list = None):
        self.release = release
        self.policy_version = policy_version
        self.rules = custom_rules or self.DEFAULT_RULES

    def evaluate(self, comparison: ComparisonResult) -> tuple[str, list[PolicyRuleResult]]:
        """
        Evaluate all rules against the release and comparison.

        Returns:
            (overall_status, rule_results)
            overall_status: 'green', 'yellow', or 'red'
        """
        rule_results = []
        has_blocking_failure = False
        has_warning = False

        for rule_def in self.rules:
            result = self._evaluate_rule(rule_def, comparison)
            rule_results.append(result)

            if not result.passed:
                if rule_def.get('severity') == 'blocking':
                    has_blocking_failure = True
                elif rule_def.get('severity') == 'warning':
                    has_warning = True

        # Determine overall status
        if has_blocking_failure:
            overall_status = ReleaseAnalysis.Status.RED
        elif has_warning:
            overall_status = ReleaseAnalysis.Status.YELLOW
        else:
            overall_status = ReleaseAnalysis.Status.GREEN

        return overall_status, rule_results

    def _evaluate_rule(self, rule_def: dict, comparison: ComparisonResult) -> PolicyRuleResult:
        """Evaluate a single rule."""
        rule_id = rule_def['id']

        if rule_id == 'required_tests_pass':
            return self._check_required_tests(comparison)
        elif rule_id == 'no_new_failures':
            return self._check_no_new_failures(comparison)
        elif rule_id == 'critical_health_checks':
            return self._check_critical_health_checks()
        elif rule_id == 'no_persistent_failures':
            return self._check_no_persistent_failures(comparison)
        elif rule_id == 'flaky_test_threshold':
            return self._check_flaky_threshold(comparison, rule_def.get('threshold', 0.05))
        elif rule_id == 'test_duration_anomaly':
            return self._check_duration_anomaly()
        else:
            return PolicyRuleResult(
                rule=rule_id,
                passed=True,
                message=f'Unknown rule: {rule_id}',
                warning=True,
            )

    def _check_required_tests(self, comparison: ComparisonResult) -> PolicyRuleResult:
        """All required tests must pass (no failures at all)."""
        total_failures = len(comparison.new_failures) + len(comparison.persistent_failures)

        if total_failures == 0:
            return PolicyRuleResult(
                rule='required_tests_pass',
                passed=True,
                message='All tests passed',
                details={'total_failures': 0},
            )
        else:
            return PolicyRuleResult(
                rule='required_tests_pass',
                passed=False,
                message=f'{total_failures} test(s) failed',
                details={
                    'total_failures': total_failures,
                    'new_failures': len(comparison.new_failures),
                    'persistent_failures': len(comparison.persistent_failures),
                },
            )

    def _check_no_new_failures(self, comparison: ComparisonResult) -> PolicyRuleResult:
        """No new failures compared to previous release."""
        new_failure_count = len(comparison.new_failures)

        if new_failure_count == 0:
            return PolicyRuleResult(
                rule='no_new_failures',
                passed=True,
                message='No new failures',
                details={'new_failures': 0},
            )
        else:
            return PolicyRuleResult(
                rule='no_new_failures',
                passed=False,
                message=f'{new_failure_count} new failure(s) detected',
                details={
                    'new_failures': new_failure_count,
                    'failed_tests': [f'{tc.classname}.{tc.name}' for tc in comparison.new_failures],
                },
            )

    def _check_critical_health_checks(self) -> PolicyRuleResult:
        """Check if critical API health checks pass."""
        # Check if there are any critical API checks configured for this project
        from apps.api_checks.models import ApiCheck, ApiCheckResult
        from django.utils import timezone
        from datetime import timedelta

        critical_checks = ApiCheck.objects.filter(
            project=self.release.project,
            is_active=True,
            is_critical=True,
        )

        if not critical_checks.exists():
            return PolicyRuleResult(
                rule='critical_health_checks',
                passed=True,
                message='No critical health checks configured',
                details={'configured': False, 'critical_checks': 0},
                warning=True,
            )

        # Check the latest result of each critical check
        failing_critical = []
        for check in critical_checks:
            latest_result = check.results.filter(
                triggered_by__in=['scheduled', 'release', 'manual']
            ).order_by('-created_at').first()

            if not latest_result or latest_result.status != ApiCheckResult.Status.SUCCESS:
                failing_critical.append({
                    'check_name': check.name,
                    'url': check.url,
                    'last_status': latest_result.status if latest_result else 'never_run',
                })

        if failing_critical:
            return PolicyRuleResult(
                rule='critical_health_checks',
                passed=False,
                message=f'{len(failing_critical)} critical health check(s) failing',
                details={
                    'configured': True,
                    'critical_checks': critical_checks.count(),
                    'failing': failing_critical,
                },
            )
        else:
            return PolicyRuleResult(
                rule='critical_health_checks',
                passed=True,
                message=f'All {critical_checks.count()} critical health checks passing',
                details={'configured': True, 'critical_checks': critical_checks.count()},
            )

    def _check_no_persistent_failures(self, comparison: ComparisonResult) -> PolicyRuleResult:
        """Warn if tests fail persistently across releases."""
        persistent_count = len(comparison.persistent_failures)

        if persistent_count == 0:
            return PolicyRuleResult(
                rule='no_persistent_failures',
                passed=True,
                message='No persistent failures',
                details={'persistent_failures': 0},
            )
        else:
            return PolicyRuleResult(
                rule='no_persistent_failures',
                passed=False,
                message=f'{persistent_count} persistent failure(s)',
                details={
                    'persistent_failures': persistent_count,
                    'failed_tests': [f'{tc.classname}.{tc.name}' for tc in comparison.persistent_failures],
                },
                warning=True,
            )

    def _check_flaky_threshold(self, comparison: ComparisonResult, threshold: float) -> PolicyRuleResult:
        """Check if flaky test rate exceeds threshold."""
        # Flaky = test that changes status between releases (pass<->fail)
        # For 2-release comparison: tests that passed in one and failed in the other
        # A proper implementation would track history across multiple releases
        current_run = self.release.test_runs.filter(status=TestRun.Status.COMPLETED).first()
        if not current_run or current_run.total_tests == 0:
            return PolicyRuleResult(
                rule='flaky_test_threshold',
                passed=True,
                message='No test data for flaky analysis',
                details={'flaky_rate': 0, 'threshold': threshold},
            )

        # Get current and previous test results by identifier
        current_results = {f"{tc.classname}.{tc.name}": tc for tc in comparison.new_failures + comparison.persistent_failures + comparison.unchanged_passing}
        # We need previous results too - get from previous release
        prev_run = self.release.previous_release.test_runs.filter(status=TestRun.Status.COMPLETED).first() if self.release.previous_release else None
        if not prev_run:
            return PolicyRuleResult(
                rule='flaky_test_threshold',
                passed=True,
                message='No previous release for flaky analysis',
                details={'flaky_rate': 0, 'threshold': threshold},
            )

        # Only fetch classname, name, and status from DB to avoid loading full objects
        prev_results_qs = prev_run.test_cases.all().values('classname', 'name', 'status')
        prev_results = {f"{r['classname']}.{r['name']}": r['status'] for r in prev_results_qs}

        # Find tests that exist in both but have different pass/fail status
        flaky_candidates = set()
        for identifier, current_tc in current_results.items():
            if identifier in prev_results:
                prev_passed = prev_results[identifier] in (TestCaseResult.Status.PASSED, TestCaseResult.Status.XPASS)
                current_passed = current_tc.is_passed
                if current_passed != prev_passed:
                    flaky_candidates.add(identifier)

        flaky_count = len(flaky_candidates)
        flaky_rate = flaky_count / current_run.total_tests if current_run.total_tests > 0 else 0

        if flaky_rate <= threshold:
            return PolicyRuleResult(
                rule='flaky_test_threshold',
                passed=True,
                message=f'Flaky rate {flaky_rate:.1%} within threshold {threshold:.1%}',
                details={'flaky_count': flaky_count, 'flaky_rate': flaky_rate, 'threshold': threshold},
            )
        else:
            return PolicyRuleResult(
                rule='flaky_test_threshold',
                passed=False,
                message=f'Flaky rate {flaky_rate:.1%} exceeds threshold {threshold:.1%}',
                details={'flaky_count': flaky_count, 'flaky_rate': flaky_rate, 'threshold': threshold},
                warning=True,
            )

    def _check_duration_anomaly(self) -> PolicyRuleResult:
        """Check if test duration is anomalous."""
        current_run = self.release.test_runs.filter(status=TestRun.Status.COMPLETED).first()
        if not current_run:
            return PolicyRuleResult(
                rule='test_duration_anomaly',
                passed=True,
                message='No duration data',
                details={'duration': 0},
            )

        # Compare to previous release
        if self.release.previous_release:
            prev_run = self.release.previous_release.test_runs.filter(
                status=TestRun.Status.COMPLETED
            ).first()
            if prev_run and prev_run.total_duration > 0:
                ratio = current_run.total_duration / prev_run.total_duration
                # Warn if > 2x slower
                if ratio > 2.0:
                    return PolicyRuleResult(
                        rule='test_duration_anomaly',
                        passed=False,
                        message=f'Test duration {ratio:.1f}x previous release',
                        details={'current': current_run.total_duration, 'previous': prev_run.total_duration, 'ratio': ratio},
                        warning=True,
                    )

        return PolicyRuleResult(
            rule='test_duration_anomaly',
            passed=True,
            message='Duration within normal range',
            details={'duration': current_run.total_duration},
        )


class TestRunProcessingService:
    """
    Service for processing uploaded JUnit XML test runs.

    Handles parsing, storage, fingerprinting, and triggering analysis.
    """

    def __init__(self, release: Release):
        self.release = release

    @transaction.atomic
    def process_upload(self, xml_content: str, test_run_name: str, idempotency_key: str) -> TestRun:
        """
        Process JUnit XML upload: parse, store, compute fingerprints.

        Returns created/updated TestRun.
        """
        # Parse XML
        parsed = parse_junit_xml(xml_content)

        # Get or create test run (idempotent)
        test_run, created = TestRun.objects.get_or_create(
            release=self.release,
            idempotency_key=idempotency_key,
            defaults={
                'name': test_run_name,
                'status': TestRun.Status.PROCESSING,
            }
        )

        if not created:
            # Update existing
            test_run.name = test_run_name
            test_run.status = TestRun.Status.PROCESSING
            test_run.raw_xml = xml_content
            test_run.xml_size = len(xml_content.encode('utf-8'))
            test_run.save()

        # Clear existing test cases for this run
        test_run.test_cases.all().delete()

        # Create test case results
        test_cases_to_create = []
        for suite in parsed.test_suites:
            for tc in suite.test_cases:
                fingerprint = generate_test_fingerprint(tc.classname, tc.name, tc.traceback)

                test_cases_to_create.append(TestCaseResult(
                    test_run=test_run,
                    classname=tc.classname,
                    name=tc.name,
                    status=tc.status,
                    duration=tc.duration,
                    message=tc.message,
                    output=tc.output,
                    traceback=tc.traceback,
                    fingerprint=fingerprint,
                    properties=tc.properties,
                ))

        TestCaseResult.objects.bulk_create(test_cases_to_create)

        # Update test run summary
        test_run.total_tests = parsed.total_tests
        test_run.passed_tests = parsed.passed_tests
        test_run.failed_tests = parsed.failed_tests
        test_run.skipped_tests = parsed.skipped_tests
        test_run.error_tests = parsed.error_tests
        test_run.total_duration = parsed.total_duration
        test_run.raw_xml = xml_content
        test_run.xml_size = len(xml_content.encode('utf-8'))
        test_run.status = TestRun.Status.COMPLETED
        test_run.finished_at = timezone.now()
        test_run.save()

        logger.info(
            'Processed test run %s for release %s: %d tests, %d failed',
            test_run.name, self.release, parsed.total_tests, parsed.failed_tests + parsed.error_tests
        )

        return test_run


class ReleaseAnalysisService:
    """
    Service for generating release analysis (policy evaluation).
    """

    @transaction.atomic
    def analyze(self, release: Release, policy_version: str = '1.0') -> ReleaseAnalysis:
        """
        Generate release analysis by comparing with previous release and evaluating policy.
        """
        # Get comparison
        comparison_service = ReleaseComparisonService(release)
        comparison = comparison_service.compare()

        # Evaluate policy
        engine = PolicyEngine(release, policy_version)
        status, rule_results = engine.evaluate(comparison)

        # Create or update analysis
        analysis, created = ReleaseAnalysis.objects.update_or_create(
            release=release,
            defaults={
                'status': status,
                'policy_version': policy_version,
                'rule_results': [
                    {
                        'rule': r.rule,
                        'passed': r.passed,
                        'message': r.message,
                        'details': r.details,
                        'warning': r.warning,
                    }
                    for r in rule_results
                ],
                'new_failures': len(comparison.new_failures),
                'persistent_failures': len(comparison.persistent_failures),
                'fixed_failures': len(comparison.fixed_failures),
                'flaky_tests': 0,  # Computed in policy
                'compared_to_release': comparison_service.previous_release,
                'evaluated_at': timezone.now(),
            }
        )

        logger.info(
            'Release analysis for %s: %s (%d rules)',
            release, analysis.get_status_display(), len(rule_results)
        )

        return analysis