"""
Populate rich sample data into ReleaseGuard for demonstration and testing.
"""

import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'releaseguard.settings')
django.setup()

from django.utils import timezone
from apps.projects.models import Project, Environment
from apps.releases.models import Release, TestRun, TestCaseResult, ReleaseAnalysis
from apps.api_checks.models import ApiCheck, ApiCheckResult
from apps.issues.models import IssueGroup, ErrorEvent
from apps.dashboard.models import DashboardSnapshot

project = Project.objects.first()
if not project:
    print("No project found!")
    exit(1)

# Clear existing snapshots
DashboardSnapshot.objects.filter(project=project).delete()

env_prod = Environment.objects.filter(project=project, name='Production').first()
env_dev = Environment.objects.filter(project=project, name='Development').first() or env_prod
now = timezone.now()

print(f"Seeding demo data for project: {project.name}...")

# 1. Releases
releases_meta = [
    ('v1.0.0', 'main', 'Initial production launch', 'green', 14),
    ('v1.1.0', 'main', 'Add user authentication & profile API', 'green', 10),
    ('v1.2.0', 'main', 'Add payment gateway integration', 'yellow', 6),
    ('v1.2.1', 'main', 'Hotfix payment webhook verification', 'green', 3),
    ('v1.3.0', 'main', 'Order processing v2 performance upgrade', 'green', 1),
]

created_releases = []
for version, branch, msg, status, days_ago in releases_meta:
    dep_time = now - timedelta(days=days_ago)
    rel, _ = Release.objects.get_or_create(
        project=project,
        version=version,
        defaults={
            'environment': env_prod,
            'branch': branch,
            'workflow_run_id': f"run_{version.replace('.', '_')}",
            'commit_sha': f"abc{version.replace('.', '')}def789012345678901234567890",
            'commit_short_sha': f"abc{version.replace('.', '')[:3]}",
            'commit_message': msg,
            'commit_author': 'DevOps Lead <dev@company.com>',
            'deployed_at': dep_time,
        }
    )
    created_releases.append(rel)

    # Test runs for each release
    passed = 48 if status == 'green' else 45
    failed = 0 if status == 'green' else 3
    tr, _ = TestRun.objects.get_or_create(
        release=rel,
        name='pytest-ci-suite',
        defaults={
            'status': 'completed',
            'total_tests': passed + failed,
            'passed_tests': passed,
            'failed_tests': failed,
            'skipped_tests': 2,
            'error_tests': 0,
            'total_duration': 42.5,
            'started_at': dep_time - timedelta(minutes=10),
            'finished_at': dep_time - timedelta(minutes=5),
        }
    )

    # Release Analysis
    ReleaseAnalysis.objects.get_or_create(
        release=rel,
        defaults={
            'status': status,
            'policy_version': '1.0.0',
            'rule_results': {
                'min_pass_rate': {'passed': status != 'red', 'expected': 95.0, 'actual': (passed / (passed + failed) * 100)},
                'no_new_critical_failures': {'passed': status == 'green'},
            },
            'new_failures': 0 if status == 'green' else 2,
            'persistent_failures': 0,
            'fixed_failures': 1 if status == 'green' else 0,
            'flaky_tests': 1 if status == 'yellow' else 0,
            'evaluated_at': dep_time,
        }
    )

print(f"Created {len(created_releases)} releases with test runs & analyses.")

# 2. API Checks
checks_data = [
    ("Auth Health Endpoint", "https://httpbin.org/status/200", 200, 30),
    ("Checkout Service Check", "https://httpbin.org/status/200", 200, 60),
    ("Catalog Inventory API", "https://httpbin.org/status/200", 200, 60),
]

for name, url, expected_status, interval in checks_data:
    check, _ = ApiCheck.objects.get_or_create(
        project=project,
        name=name,
        defaults={
            'environment': env_prod,
            'url': url,
            'method': 'GET',
            'expected_status': expected_status,
            'interval_seconds': interval,
            'is_active': True,
            'is_critical': True,
            'last_run_at': now - timedelta(minutes=2),
        }
    )

    # Add a recent successful result
    ApiCheckResult.objects.get_or_create(
        api_check=check,
        defaults={
            'status': 'success',
            'status_code': 200,
            'latency_ms': 142.0,
            'dns_lookup_ms': 12.0,
            'connect_ms': 35.0,
            'tls_handshake_ms': 45.0,
            'ssl_valid': True,
        }
    )

print("Created 3 active API checks with live results.")

# 3. Issue Groups
issues_data = [
    (
        "RedisConnectionError: Timeout connecting to cache-cluster-01",
        "redis.exceptions.ConnectionError",
        "open",
        24,
        True
    ),
    (
        "PaymentGatewayTimeout: Stripe webhook response exceeded 5000ms",
        "stripe.error.APIConnectionError",
        "in_progress",
        8,
        False
    ),
    (
        "InvalidTokenSignature: Expired JWT claims in refresh route",
        "jwt.exceptions.ExpiredSignatureError",
        "resolved",
        41,
        False
    ),
]

for title, exc_class, status, occurrences, is_regr in issues_data:
    import hashlib
    fp = hashlib.sha256(title.encode('utf-8')).hexdigest()[:32]
    IssueGroup.objects.get_or_create(
        project=project,
        fingerprint=fp,
        defaults={
            'title': title,
            'exception_class': exc_class,
            'error_type': exc_class.split('.')[-1],
            'status': status,
            'is_regression': is_regr,
            'occurrence_count': occurrences,
            'first_seen_at': now - timedelta(days=5),
            'last_seen_at': now - timedelta(hours=1),
            'first_seen_release': created_releases[-2],
            'last_seen_release': created_releases[-1],
            'tags': {'severity': 'high' if is_regr else 'medium', 'team': 'backend'},
        }
    )

print("Created 3 error issue groups.")
print("Demo seeding complete!")
