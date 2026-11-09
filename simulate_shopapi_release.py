"""
Simulate a release of the shopapi_project demo service into ReleaseGuard.
This runs tests, ingests JUnit XML, simulates API checks, and captures error incidents.
"""

import os
import sys
import hashlib
import subprocess
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'releaseguard.settings')
django.setup()

from django.utils import timezone
from apps.projects.models import Project, Environment
from apps.releases.models import Release, TestRun, TestCaseResult, ReleaseAnalysis
from apps.releases.services import TestRunProcessingService, ReleaseAnalysisService
from apps.api_checks.models import ApiCheck, ApiCheckResult
from apps.issues.models import IssueGroup, ErrorEvent
from apps.dashboard.models import DashboardSnapshot

def run_simulation():
    project = Project.objects.first()
    if not project:
        print("[-] No project found in ReleaseGuard. Please ensure Demo Project exists.")
        return

    prod_env = Environment.objects.filter(project=project, name='Production').first()
    if not prod_env:
        prod_env = Environment.objects.filter(project=project).first()

    print(f"[*] Targeting Project: {project.name} ({project.id})")
    print(f"[*] Environment: {prod_env.name}")

    # 1. Run shopapi_project tests and produce results.xml
    shopapi_dir = os.path.join(os.path.dirname(__file__), 'shopapi_project')
    test_file = os.path.join(shopapi_dir, 'shop', 'tests', 'test_regressions.py')
    results_xml = os.path.join(shopapi_dir, 'results.xml')

    print("[*] Running shopapi_project regression tests with pytest...")
    python_exe = sys.executable
    cmd = [python_exe, '-m', 'pytest', test_file, f'--junitxml={results_xml}', '-q']
    proc = subprocess.run(cmd, cwd=shopapi_dir, capture_output=True, text=True)
    print(f"[+] Tests execution finished. Result file exists: {os.path.exists(results_xml)}")

    if not os.path.exists(results_xml):
        print("[-] Failed to find JUnit XML results file.")
        return

    with open(results_xml, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    # 2. Register new Release
    release_version = "v2.0.0-shopapi"
    now = timezone.now()
    
    release, created = Release.objects.get_or_create(
        project=project,
        version=release_version,
        defaults={
            'environment': prod_env,
            'branch': 'release/shopapi-v2',
            'workflow_run_id': f"shopapi_{int(now.timestamp())}",
            'commit_sha': "a9f3b140283c74829104857bca19482701928374",
            'commit_short_sha': "a9f3b14",
            'commit_message': "feat(shopapi): deploy shopapi e-commerce checkout with regression suite",
            'commit_author': "Release Engineer <re@releaseguard.dev>",
            'deployed_at': now,
        }
    )
    if not created:
        release.deployed_at = now
        release.save()

    print(f"[+] Release registered: {release.version} (ID: {release.id})")

    # 3. Process test run upload
    processor = TestRunProcessingService(release)
    test_run = processor.process_upload(
        xml_content=xml_content,
        test_run_name="shopapi-regression-suite",
        idempotency_key=f"shopapi-suite-{int(now.timestamp())}",
    )
    print(f"[+] Ingested test run '{test_run.name}': {test_run.total_tests} tests ({test_run.passed_tests} passed, {test_run.failed_tests} failed, {test_run.skipped_tests} skipped)")

    # 4. Run Release Analysis
    analysis_service = ReleaseAnalysisService()
    analysis = analysis_service.analyze(release)
    print(f"[+] Release analysis completed: Health status = {analysis.status.upper()}")

    # 5. Connect API Checks for ShopAPI endpoints
    api_checks_data = [
        ("ShopAPI Calculate Total API", "http://127.0.0.1:8001/api/regressions/calculate-total/", "POST", 200, 45, ApiCheckResult.Status.SUCCESS),
        ("ShopAPI Broken Orders Endpoint", "http://127.0.0.1:8001/api/regressions/broken-endpoint/", "GET", 500, 620, ApiCheckResult.Status.FAILURE),
        ("ShopAPI Heavy Analytics Report", "http://127.0.0.1:8001/api/regressions/heavy-report/", "GET", 200, 1850, ApiCheckResult.Status.SUCCESS),
        ("ShopAPI External Payment Gateway", "http://127.0.0.1:8001/api/regressions/external-payment/", "POST", 503, 120, ApiCheckResult.Status.FAILURE),
    ]

    for name, url, method, status_code, response_time, check_status in api_checks_data:
        check, _ = ApiCheck.objects.get_or_create(
            project=project,
            name=name,
            defaults={
                'url': url,
                'method': method,
                'interval_seconds': 60,
                'timeout_seconds': 10,
                'expected_status': 200,
                'is_active': True,
                'is_critical': True if status_code == 500 else False,
            }
        )
        ApiCheckResult.objects.create(
            api_check=check,
            status=check_status,
            latency_ms=response_time,
            status_code=status_code,
            error_message="HTTP 500 NameError: TaxService not defined" if status_code == 500 else ("503 Service Unavailable" if status_code == 503 else ""),
            triggered_by='release',
        )

    print(f"[+] Generated {len(api_checks_data)} API check health data points")

    # 6. Capture Error Incidents from regressions
    fp1 = hashlib.sha256(b"NameError:TaxService").hexdigest()
    issue1, _ = IssueGroup.objects.get_or_create(
        project=project,
        fingerprint=fp1,
        defaults={
            'title': "NameError: name 'TaxService' is not defined",
            'exception_class': "NameError",
            'error_type': "CRITICAL",
            'status': IssueGroup.Status.OPEN,
            'first_seen_at': now - timedelta(hours=2),
            'last_seen_at': now,
            'occurrence_count': 42,
            'first_seen_release': release,
            'last_seen_release': release,
        }
    )
    issue1.status = IssueGroup.Status.OPEN
    issue1.last_seen_at = now
    issue1.occurrence_count += 1
    issue1.last_seen_release = release
    issue1.save()

    ErrorEvent.objects.create(
        issue_group=issue1,
        project=project,
        release=release,
        environment=prod_env,
        source=ErrorEvent.Source.API_CHECK,
        fingerprint=fp1,
        exception_class="NameError",
        message="NameError: name 'TaxService' is not defined in shop/views.py at line 48 in broken_endpoint",
        traceback="Traceback (most recent call last):\n  File \"shop/views.py\", line 48, in broken_endpoint\n    tax = TaxService.calculate(subtotal)\nNameError: name 'TaxService' is not defined",
        context={"endpoint": "/api/regressions/broken-endpoint/", "method": "GET", "status_code": 500},
        occurred_at=now,
    )

    fp2 = hashlib.sha256(b"PaymentGatewayException:503").hexdigest()
    issue2, _ = IssueGroup.objects.get_or_create(
        project=project,
        fingerprint=fp2,
        defaults={
            'title': "PaymentGatewayException: 503 Service Unavailable",
            'exception_class': "PaymentGatewayException",
            'error_type': "HIGH",
            'status': IssueGroup.Status.OPEN,
            'first_seen_at': now - timedelta(hours=1),
            'last_seen_at': now,
            'occurrence_count': 18,
            'first_seen_release': release,
            'last_seen_release': release,
        }
    )
    issue2.last_seen_at = now
    issue2.occurrence_count += 1
    issue2.last_seen_release = release
    issue2.save()

    ErrorEvent.objects.create(
        issue_group=issue2,
        project=project,
        release=release,
        environment=prod_env,
        source=ErrorEvent.Source.API_CHECK,
        fingerprint=fp2,
        exception_class="PaymentGatewayException",
        message="PaymentGatewayException: External payment dependency failed with 503 Service Unavailable",
        traceback="Traceback (most recent call last):\n  File \"shop/views.py\", line 82, in external_payment\n    raise ServiceUnavailable('Upstream gateway down')\nServiceUnavailable: Upstream gateway down",
        context={"endpoint": "/api/regressions/external-payment/", "method": "POST", "status_code": 503},
        occurred_at=now,
    )

    # 7. Invalidate old cached snapshots
    DashboardSnapshot.objects.filter(project=project).delete()
    print("[+] Cleared cached dashboard snapshots.")
    print("\n" + "="*60)
    print(f"SUCCESS: ShopAPI demo release '{release.version}' successfully ingested!")
    print(f"- Release Detail: http://localhost:3000/releases/{release.id}")
    print(f"- Releases List:   http://localhost:3000/releases")
    print(f"- Issues/Incidents:http://localhost:3000/issues")
    print(f"- API Checks:      http://localhost:3000/api-checks")
    print(f"- Dashboard:       http://localhost:3000/dashboard")
    print("="*60)

if __name__ == '__main__':
    run_simulation()
