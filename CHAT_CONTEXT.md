# ReleaseGuard Project - Chat Context

## Project Overview
**ReleaseGuard** - Software Release Reliability & Incident Intelligence Platform for small Python teams.

**Location:** `D:\Release Guard`

## Current Status (as of last session)
- ✅ **All 97 tests pass** (ReleaseGuard core)
- ✅ **12/12 ShopAPI tests pass** (from original location)
- ✅ **Server runs** at `http://127.0.0.1:8000/api/v1/`
- ✅ **Background worker** functional: `python manage.py runworker --interval 5`
- ✅ **All 109 tests pass** (97 core + 12 ShopAPI)

## Project Structure
```
D:\Release Guard\
├── apps/
│   ├── core/           # Base models, permissions, exceptions, BackgroundJob
│   ├── accounts/       # Custom User (email auth)
│   ├── organizations/  # Organisation, Membership
│   ├── projects/       # Project, Environment, ProjectToken
│   ├── releases/       # Release, TestRun, TestCaseResult, ReleaseAnalysis
│   ├── api_checks/     # ApiCheck, ApiCheckResult (SSRF-protected)
│   ├── issues/         # IssueGroup, ErrorEvent (fingerprint grouping)
│   ├── ml/             # MLModel, ModelPrediction, TrainingDataset, FeatureStore
│   └── dashboard/      # DashboardView, WidgetConfig, UserDashboardPreference
├── releaseguard/       # Django settings, URLs, WSGI
├── shopapi_project/    # Demo app with 6 deliberate regressions
├── .github/workflows/ci.yml
├── Dockerfile / docker-compose.yml
└── README.md
```

## Key Commands
```bash
# Activate venv
.venv\Scripts\Activate.ps1

# Run server
python manage.py runserver 127.0.0.1:8000

# Background worker
python manage.py runworker --interval 5

# Tests
pytest apps/
pytest shopapi_project/shop/tests/
```

## API Endpoints (Project-scoped)
```
POST   /api/v1/projects/{pk}/releases/                    # Register release
POST   /api/v1/projects/{pk}/releases/{id}/test-runs/    # Upload JUnit XML
GET    /api/v1/projects/{pk}/releases/{id}/compare/      # Compare releases
GET    /api/v1/projects/{pk}/dashboard/overview/         # Dashboard
GET    /api/v1/projects/{pk}/api-checks/                 # API health checks
GET    /api/v1/projects/{pk}/issues/                     # Issue groups
```

## Key Endpoints Verified
- **API Root**: http://127.0.0.1:8000/api/v1/
- **Health**: http://127.0.0.1:8000/api/v1/health/
- **Admin**: http://127.0.0.1:8000/admin/

## Recent Fixes Applied
1. ✅ Fixed SQLite job queue race condition (BackgroundJob.claim_next_job)
2. ✅ Fixed DashboardSnapshot cache lookup (JSONField context__contains)
3. ✅ Fixed N+1 queries in dashboard release detail
4. ✅ Fixed ApiCheckScheduler scalability (PostgreSQL F expressions)
4. ✅ Implemented critical health checks in PolicyEngine
5. ✅ Fixed flaky threshold detection (using classname.name + status)
6. ✅ Fixed widget config duplication (WIDGET_CONFIGS dict)
7. ✅ Fixed ReleaseAnalysis flaky_tests field

## ShopAPI Demo (for ReleaseGuard testing)
- Location: `shopapi_project/`
- 6 deliberate regressions for testing
- 12 tests pass
- GitHub Actions workflow with ReleaseGuard integration

## Test Results
- **ReleaseGuard Core**: 97 tests ✅
- **ShopAPI Demo**: 12 tests ✅
- **Total**: 109 tests passing

## Known Issues
- ShopAPI tests have path issues from `D:\Release Guard\shopapi_project` due to space in folder name
- Workaround: Run from original location or create junction `mklink /D D:\ReleaseGuard D:\Release Guard`

## Pending (Not Yet Implemented)
- HTML Dashboard frontend (currently API-only)
- PostgreSQL production deployment
- GitHub App/OAuth integration
- Pull request comments integration