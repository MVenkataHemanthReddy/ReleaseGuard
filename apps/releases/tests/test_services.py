"""
Tests for ReleaseGuard services: comparison, policy engine, processing.
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from unittest.mock import Mock, patch

from apps.releases.services import (
    ReleaseComparisonService,
    PolicyEngine,
    TestRunProcessingService,
    ReleaseAnalysisService,
    ComparisonResult,
)
from apps.releases.models import Release, TestRun, TestCaseResult, ReleaseAnalysis
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
def previous_release(db, project, environment):
    return Release.objects.create(
        project=project,
        environment=environment,
        version='0.9.0',
        commit_sha='b' * 40,
        branch='main',
        workflow_run_id='run_122',
        deployed_at=timezone.now() - timedelta(days=1),
    )


@pytest.fixture
def test_run(db, release):
    return TestRun.objects.create(
        release=release,
        name='unit',
        status=TestRun.Status.COMPLETED,
        total_tests=10,
        passed_tests=8,
        failed_tests=2,
        idempotency_key='run_123:unit',
    )


@pytest.fixture
def test_cases(db, test_run):
    """Create test cases: 2 new failures, 1 persistent, 1 fixed, 6 passing."""
    cases = []

    # New failures (2)
    for i in range(2):
        cases.append(TestCaseResult.objects.create(
            test_run=test_run,
            classname=f'test_new_fail_{i}',
            name=f'test_method_{i}',
            status=TestCaseResult.Status.FAILED,
        ))

    # Persistent failure (1) - also in previous
    cases.append(TestCaseResult.objects.create(
        test_run=test_run,
        classname='test_persistent',
        name='test_fail',
        status=TestCaseResult.Status.FAILED,
    ))

    # Fixed failure (1) - was failing in previous, now passing
    cases.append(TestCaseResult.objects.create(
        test_run=test_run,
        classname='test_fixed',
        name='test_now_passes',
        status=TestCaseResult.Status.PASSED,
    ))

    # Unchanged passing (6)
    for i in range(6):
        cases.append(TestCaseResult.objects.create(
            test_run=test_run,
            classname=f'test_pass_{i}',
            name=f'test_method_{i}',
            status=TestCaseResult.Status.PASSED,
        ))

    return cases


@pytest.fixture
def previous_test_run(db, previous_release):
    run = TestRun.objects.create(
        release=previous_release,
        name='unit',
        status=TestRun.Status.COMPLETED,
        total_tests=8,
        passed_tests=6,
        failed_tests=2,
        idempotency_key='run_122:unit',
    )

    # Persistent failure
    TestCaseResult.objects.create(
        test_run=run,
        classname='test_persistent',
        name='test_fail',
        status=TestCaseResult.Status.FAILED,
    )

    # Fixed failure (was failing before)
    TestCaseResult.objects.create(
        test_run=run,
        classname='test_fixed',
        name='test_now_passes',
        status=TestCaseResult.Status.FAILED,
    )

    # 6 passing (same as current)
    for i in range(6):
        TestCaseResult.objects.create(
            test_run=run,
            classname=f'test_pass_{i}',
            name=f'test_method_{i}',
            status=TestCaseResult.Status.PASSED,
        )

    return run


# ==================== Comparison Service Tests ====================

class TestReleaseComparisonService:
    """Tests for ReleaseComparisonService."""

    def test_compare_with_previous(self, release, previous_release, test_cases, previous_test_run):
        """Test comparison with previous release."""
        service = ReleaseComparisonService(release)
        result = service.compare()

        # Should find previous release
        assert service.previous_release == previous_release

        # Check categories
        assert len(result.new_failures) == 2
        assert len(result.persistent_failures) == 1
        assert len(result.fixed_failures) == 1
        assert len(result.unchanged_passing) == 6

        # Verify specific tests
        new_failure_names = {f'{tc.classname}.{tc.name}' for tc in result.new_failures}
        assert 'test_new_fail_0.test_method_0' in new_failure_names
        assert 'test_new_fail_1.test_method_1' in new_failure_names

        persistent_names = {f'{tc.classname}.{tc.name}' for tc in result.persistent_failures}
        assert 'test_persistent.test_fail' in persistent_names

        fixed_names = {f'{tc.classname}.{tc.name}' for tc in result.fixed_failures}
        assert 'test_fixed.test_now_passes' in fixed_names

    def test_compare_no_previous_release(self, release, test_cases):
        """Test comparison when no previous release exists."""
        # Ensure no previous release
        Release.objects.exclude(pk=release.pk).delete()

        service = ReleaseComparisonService(release)
        result = service.compare()

        # All failures are "new" (no baseline)
        # 2 new_failures + 1 persistent + 1 fixed (now passing, no previous to compare) = 4 failures
        # Wait: without previous, the "persistent" and "fixed" are also treated as new
        # Actually: 2 new_failures + 1 persistent (failed in current, no previous) + 1 fixed (passed in current, no previous) = 3 failures
        # And 6 passing + 1 fixed (now passing) = 7 unchanged_passing
        assert len(result.new_failures) == 3
        assert len(result.persistent_failures) == 0
        assert len(result.fixed_failures) == 0
        assert len(result.unchanged_passing) == 7

    def test_compare_identifies_new_vs_persistent_correctly(self, release, previous_release, test_cases, previous_test_run):
        """Verify new vs persistent classification logic."""
        service = ReleaseComparisonService(release)
        result = service.compare()

        # New failure: failed now, not in previous (or passed in previous)
        # Persistent: failed now AND failed in previous
        # Fixed: passed now, failed in previous

        # The 2 new failures don't exist in previous
        for tc in result.new_failures:
            assert tc.status in [TestCaseResult.Status.FAILED, TestCaseResult.Status.ERROR]

        # The 1 persistent exists in both and failed in both
        for tc in result.persistent_failures:
            assert tc.status in [TestCaseResult.Status.FAILED, TestCaseResult.Status.ERROR]

        # The 1 fixed was failing in previous, now passes
        # fixed_failures returns the PREVIOUS test case (to show what was fixed)
        for tc in result.fixed_failures:
            assert tc.status in [TestCaseResult.Status.FAILED, TestCaseResult.Status.ERROR]


# ==================== Policy Engine Tests ====================

class TestPolicyEngine:
    """Tests for PolicyEngine."""

    def test_all_pass_green(self, release, previous_release):
        """All tests pass -> GREEN."""
        # Current: all pass
        test_run = TestRun.objects.create(
            release=release,
            name='unit',
            status=TestRun.Status.COMPLETED,
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            idempotency_key='run_123:unit',
        )
        for i in range(10):
            TestCaseResult.objects.create(
                test_run=test_run,
                classname=f'test_{i}',
                name=f'test_method_{i}',
                status=TestCaseResult.Status.PASSED,
            )

        # Previous also all pass
        prev_run = TestRun.objects.create(
            release=previous_release,
            name='unit',
            status=TestRun.Status.COMPLETED,
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            idempotency_key='run_122:unit',
        )
        for i in range(10):
            TestCaseResult.objects.create(
                test_run=prev_run,
                classname=f'test_{i}',
                name=f'test_method_{i}',
                status=TestCaseResult.Status.PASSED,
            )

        comparison = ReleaseComparisonService(release).compare()
        engine = PolicyEngine(release)
        status, rules = engine.evaluate(comparison)

        assert status == ReleaseAnalysis.Status.GREEN
        assert all(r.passed for r in rules)

    def test_new_failure_red(self, release, test_cases, previous_test_run):
        """New failure -> RED (blocking)."""
        comparison = ReleaseComparisonService(release).compare()
        engine = PolicyEngine(release)
        status, rules = engine.evaluate(comparison)

        assert status == ReleaseAnalysis.Status.RED

        # Check required_tests_pass failed
        req_rule = next(r for r in rules if r.rule == 'required_tests_pass')
        assert req_rule.passed is False
        assert req_rule.details['total_failures'] > 0

        # Check no_new_failures failed
        new_rule = next(r for r in rules if r.rule == 'no_new_failures')
        assert new_rule.passed is False
        assert new_rule.details['new_failures'] > 0

    def test_any_failure_is_red(self, release, previous_release):
        """Any test failure (even persistent only) -> RED because required_tests_pass is blocking."""
        # Current: 1 persistent failure, 9 passing
        test_run = TestRun.objects.create(
            release=release,
            name='unit',
            status=TestRun.Status.COMPLETED,
            total_tests=10,
            passed_tests=9,
            failed_tests=1,
            idempotency_key='run_123:unit',
        )
        TestCaseResult.objects.create(
            test_run=test_run,
            classname='test_persistent',
            name='test_fail',
            status=TestCaseResult.Status.FAILED,
        )
        for i in range(9):
            TestCaseResult.objects.create(
                test_run=test_run,
                classname=f'test_pass_{i}',
                name=f'test_method_{i}',
                status=TestCaseResult.Status.PASSED,
            )

        # Previous: same 1 persistent failure, 7 passing
        prev_run = TestRun.objects.create(
            release=previous_release,
            name='unit',
            status=TestRun.Status.COMPLETED,
            total_tests=8,
            passed_tests=7,
            failed_tests=1,
            idempotency_key='run_122:unit',
        )
        TestCaseResult.objects.create(
            test_run=prev_run,
            classname='test_persistent',
            name='test_fail',
            status=TestCaseResult.Status.FAILED,
        )
        for i in range(7):
            TestCaseResult.objects.create(
                test_run=prev_run,
                classname=f'test_pass_{i}',
                name=f'test_method_{i}',
                status=TestCaseResult.Status.PASSED,
            )

        comparison = ReleaseComparisonService(release).compare()
        engine = PolicyEngine(release)
        status, rules = engine.evaluate(comparison)

        # Any failure triggers required_tests_pass (blocking) -> RED
        assert status == ReleaseAnalysis.Status.RED

        # required_tests_pass fails (has failures)
        req_rule = next(r for r in rules if r.rule == 'required_tests_pass')
        assert req_rule.passed is False

        # no_new_failures passes (no new failures)
        new_rule = next(r for r in rules if r.rule == 'no_new_failures')
        assert new_rule.passed is True

        # no_persistent_failures fails (warning) but overall is RED due to blocking
        persist_rule = next(r for r in rules if r.rule == 'no_persistent_failures')
        assert persist_rule.passed is False
        assert persist_rule.warning is True

    def test_flaky_threshold_warning(self, release, previous_release):
        """Flaky test rate detection."""
        # Current: 5 tests failed that passed in previous (flaky candidates)
        test_run = TestRun.objects.create(
            release=release,
            name='unit',
            status=TestRun.Status.COMPLETED,
            total_tests=100,
            passed_tests=95,
            failed_tests=5,
            idempotency_key='run_123:unit',
        )

        # 5 tests that failed now but passed in previous
        for i in range(5):
            TestCaseResult.objects.create(
                test_run=test_run,
                classname=f'test_flaky_{i}',
                name='test_method',
                status=TestCaseResult.Status.FAILED,
            )
        for i in range(95):
            TestCaseResult.objects.create(
                test_run=test_run,
                classname=f'test_pass_{i}',
                name=f'test_method_{i}',
                status=TestCaseResult.Status.PASSED,
            )

        # Previous: all 100 passed (including the 5 that now fail)
        prev_run = TestRun.objects.create(
            release=previous_release,
            name='unit',
            status=TestRun.Status.COMPLETED,
            total_tests=100,
            passed_tests=100,
            failed_tests=0,
            idempotency_key='run_122:unit',
        )
        for i in range(100):
            TestCaseResult.objects.create(
                test_run=prev_run,
                classname=f'test_pass_{i}',
                name=f'test_method_{i}',
                status=TestCaseResult.Status.PASSED,
            )
        # The 5 flaky ones passed in previous
        for i in range(5):
            TestCaseResult.objects.create(
                test_run=prev_run,
                classname=f'test_flaky_{i}',
                name='test_method',
                status=TestCaseResult.Status.PASSED,
            )

        comparison = ReleaseComparisonService(release).compare()
        engine = PolicyEngine(release)
        status, rules = engine.evaluate(comparison)

        flaky_rule = next(r for r in rules if r.rule == 'flaky_test_threshold')
        # Flaky rate = 5/100 = 5% (at threshold)
        assert flaky_rule.details['flaky_rate'] == 0.05
        # At threshold, it passes (not > threshold)
        assert flaky_rule.passed is True


# ==================== Processing Service Tests ====================

class TestTestRunProcessingService:
    """Tests for TestRunProcessingService."""

    def test_process_upload_creates_test_run(self, release):
        """Process JUnit XML upload creates TestRun with cases."""
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="unit" tests="2" failures="1" time="0.5">
  <testcase classname="test_a" name="test_one" time="0.2"/>
  <testcase classname="test_b" name="test_two" time="0.3">
    <failure message="AssertionError">Failed</failure>
  </testcase>
</testsuite>'''

        service = TestRunProcessingService(release)
        test_run = service.process_upload(xml, 'unit', 'run_123:unit')

        assert test_run.name == 'unit'
        assert test_run.status == TestRun.Status.COMPLETED
        assert test_run.total_tests == 2
        assert test_run.passed_tests == 1
        assert test_run.failed_tests == 1
        assert test_run.test_cases.count() == 2

    def test_process_upload_idempotent(self, release):
        """Same idempotency key updates existing test run."""
        xml1 = '''<testsuite name="x" tests="1"><testcase name="t"/></testsuite>'''
        xml2 = '''<testsuite name="x" tests="2"><testcase name="t"/><testcase name="t2"/></testsuite>'''

        service = TestRunProcessingService(release)

        run1 = service.process_upload(xml1, 'unit', 'idem_key')
        assert run1.total_tests == 1

        run2 = service.process_upload(xml2, 'unit', 'idem_key')
        assert run2.id == run1.id  # Same object
        assert run2.total_tests == 2  # Updated

    def test_fingerprint_generated(self, release):
        """Test cases get fingerprints for error grouping."""
        xml = '''<testsuite name="x" tests="1" time="0.1">
  <testcase classname="test_a" name="test_fail" time="0.1">
    <failure message="Error">Traceback in file.py line 10</failure>
  </testcase>
</testsuite>'''

        service = TestRunProcessingService(release)
        test_run = service.process_upload(xml, 'unit', 'idem_key')

        tc = test_run.test_cases.first()
        assert tc.fingerprint != ''
        assert len(tc.fingerprint) == 32  # SHA256 truncated


# ==================== Analysis Service Tests ====================

class TestReleaseAnalysisService:
    """Tests for ReleaseAnalysisService."""

    def test_analyze_creates_analysis(self, release, test_cases, previous_test_run):
        """Analyze creates ReleaseAnalysis with policy evaluation."""
        service = ReleaseAnalysisService()
        analysis = service.analyze(release)

        assert analysis.release == release
        assert analysis.status in [ReleaseAnalysis.Status.GREEN, ReleaseAnalysis.Status.YELLOW, ReleaseAnalysis.Status.RED]
        assert analysis.policy_version == '1.0'
        assert len(analysis.rule_results) > 0
        assert analysis.evaluated_at is not None
        # compared_to_release should be the previous release
        assert analysis.compared_to_release is not None
        assert analysis.compared_to_release.version == '0.9.0'

    def test_analyze_idempotent(self, release, test_cases, previous_test_run):
        """Re-analyzing updates existing analysis."""
        service = ReleaseAnalysisService()

        analysis1 = service.analyze(release)
        analysis2 = service.analyze(release)

        assert analysis1.id == analysis2.id
        assert analysis1.status == analysis2.status

    def test_rule_results_structure(self, release, test_cases, previous_test_run):
        """Rule results have expected structure."""
        service = ReleaseAnalysisService()
        analysis = service.analyze(release)

        for rule in analysis.rule_results:
            assert 'rule' in rule
            assert 'passed' in rule
            assert 'message' in rule
            assert 'details' in rule
            assert 'warning' in rule


# Run with: pytest apps/releases/tests/test_services.py -v