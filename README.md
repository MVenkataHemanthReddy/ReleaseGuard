# ReleaseGuard

> Software Release Reliability & Incident Intelligence Platform for small Python teams.

Correlates CI test results, release metadata, API health checks, and recurring errors. Compares releases, identifies regressions, and provides explainable release assessments with optional ML-assisted insights.

## Status: All Phases Complete ✅

- [x] **Phase 1**: Django + DRF project skeleton, core models, auth
- [x] **Phase 2**: Release registration, JUnit XML ingestion
- [x] **Phase 3**: Test comparison, deterministic release policy
- [x] **Phase 4**: API health checks, background worker
- [x] **Phase 5**: Error fingerprinting, issue grouping
- [x] **Phase 6**: ML experiments (anomaly detection, clustering, classification)
- [x] **Phase 7**: Dashboard completion (overview, release detail, API health, test intelligence, issues)
- [x] **Phase 8**: Hardening, CI/CD, deployment, pilot preparation

---

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16+ (for production)

### Development Setup

```bash
# Clone (when repo exists)
git clone <repo-url>
cd releaseguard

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (DATABASE_URL, SECRET_KEY, etc.)

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser --email you@example.com --full_name "Your Name"

# Start development server
python manage.py runserver 0.0.0.0:8000

# Start background worker (separate terminal)
python manage.py runworker
```

### Session Startup (Required)
**Every new session must begin by reading the context files:**

```bash
# 1. Read session startup instructions
cat SESSION_STARTUP.md

# 2. Read full project context
cat CHAT_CONTEXT.md

# Then start working
.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8000
```

### Access
- **API Root**: http://127.0.0.1:8000/api/v1/
- **Admin**: http://127.0.0.1:8000/admin/ (superuser credentials)
- **Health**: http://127.0.0.1:8000/api/v1/health/

---

## Configuration

### Environment Variables (`.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | **Required** |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Database connection string | `sqlite:///db.sqlite3` |
| `EMAIL_BACKEND` | Email backend | `console` |
| `DEFAULT_FROM_EMAIL` | From address for emails | `ReleaseGuard <noreply@releaseguard.local>` |

### Database URL Formats

```bash
# SQLite (development)
DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL (production)
DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DBNAME
```

---

## Project Structure

```
releaseguard/
├── apps/
│   ├── core/           # Base models, exceptions, permissions, background jobs
│   ├── accounts/       # Custom User model (email-based auth)
│   ├── organizations/  # Organisation, Membership (multi-tenancy)
│   ├── projects/       # Project, Environment, ProjectToken (ingestion auth)
│   ├── releases/       # Release, TestRun, TestCaseResult, ReleaseAnalysis
│   ├── api_checks/     # ApiCheck, ApiCheckResult (health checks)
│   ├── issues/         # IssueGroup, ErrorEvent (error grouping)
│   ├── ml/             # MLModel, ModelPrediction, TrainingDataset, FeatureStore
│   └── dashboard/      # DashboardView, WidgetConfig, UserDashboardPreference
├── releaseguard/       # Project settings, URLs, WSGI
├── templates/          # Django templates (future)
├── static/             # Static files (future)
├── docs/               # Architecture, decisions, learning notes
├── .env                # Local config (gitignored)
├── .env.example        # Config template
├── requirements.txt    # Production dependencies
├── requirements-dev.txt # Dev dependencies
├── manage.py           # Django CLI
├── pytest.ini          # Test configuration
├── Dockerfile          # Multi-stage Docker build
├── docker-compose.yml  # Local development stack
├── docker-compose.prod.yml # Production stack
└── README.md
```

---

## Core Models (All Phases)

### User (Phase 1)
- Email as username (`USERNAME_FIELD = 'email'`)
- UUID PK, timestamps, soft delete
- Full name, is_active, is_staff, is_superuser

### Organisation & Membership (Phase 1)
- Organisation: Top-level tenant container with name, slug, description
- Membership: User ↔ Organisation link with roles (OWNER, ADMIN, MEMBER, VIEWER)

### Project & Environment (Phase 1)
- Project: Belongs to Organisation, has slug, description, repository_url
- Environment: Types (development, staging, production, preview, testing), base URL for health checks

### ProjectToken (Phase 1)
- Machine auth for CI/CD ingestion
- SHA-256 hash stored (never plain token)
- Prefix for identification, expiry, revocation

### Release & Test Models (Phase 2)
- Release: Version, commit SHA, branch, workflow run ID, environment
- TestRun: Summary metrics (total, passed, failed, skipped, duration)
- TestCaseResult: Individual test cases with fingerprint for grouping
- ReleaseAnalysis: Deterministic policy evaluation (GREEN/YELLOW/RED)

### API Health Checks (Phase 4)
- ApiCheck: HTTP/HTTPS endpoint configuration with scheduling
- ApiCheckResult: Status, latency breakdown, SSL validation, content matching
- SSRF protection: IP allowlist, DNS validation, redirect blocking

### Issues & Error Grouping (Phase 5)
- ErrorEvent: Individual error occurrences from test failures, API checks, manual reports
- IssueGroup: Fingerprint-based grouping with status (OPEN/IN_PROGRESS/RESOLVED/IGNORED)
- Regression detection, assignment, tagging

### ML Models (Phase 6)
- MLModel: Versioned models (IsolationForest, TF-IDF+KMeans/DBSCAN, LogisticRegression)
- ModelPrediction: Advisory predictions with human feedback loop
- TrainingDataset: Curated datasets for supervised learning
- FeatureStore: Pre-computed feature vectors for consistent training/inference

### Dashboard (Phase 7)
- DashboardView: Saved custom layouts with widgets
- WidgetConfig: 20+ widget types across 5 categories (overview, release, API health, test intelligence, issues)
- UserDashboardPreference: Per-user theme, refresh, notifications
- DashboardSnapshot: Cached data with TTL for performance

---

## API Endpoints (All Phases)

```
# Release management (Phase 2)
POST   /api/v1/projects/{project_pk}/releases/          # Register release (idempotent)
GET    /api/v1/projects/{project_pk}/releases/          # List releases
GET    /api/v1/projects/{project_pk}/releases/dashboard/ # Dashboard summary
GET    /api/v1/projects/{project_pk}/releases/{pk}/      # Release detail
GET    /api/v1/projects/{project_pk}/releases/{pk}/compare/ # Compare with previous

# Test ingestion (Phase 2)
POST   /api/v1/projects/{project_pk}/releases/{release_pk}/test-runs/  # Upload JUnit XML

# Test queries (Phase 2)
GET    /api/v1/projects/{project_pk}/test-runs/         # List test runs
GET    /api/v1/projects/{project_pk}/test-runs/{pk}/    # Test run detail
GET    /api/v1/projects/{project_pk}/test-cases/        # List test cases (filterable)
GET    /api/v1/projects/{project_pk}/analyses/          # List release analyses
GET    /api/v1/projects/{project_pk}/analyses/{pk}/     # Analysis detail

# API Health Checks (Phase 4)
POST   /api/v1/projects/{project_pk}/api-checks/        # Create health check
GET    /api/v1/projects/{project_pk}/api-checks/        # List health checks
GET    /api/v1/projects/{project_pk}/api-checks/{pk}/   # Check detail
POST   /api/v1/projects/{project_pk}/api-checks/{pk}/run/ # Manual execution
GET    /api/v1/projects/{project_pk}/api-check-results/ # List results

# Issues (Phase 5)
GET    /api/v1/projects/{project_pk}/issues/            # List issue groups
POST   /api/v1/projects/{project_pk}/issues/            # Create issue (manual)
GET    /api/v1/projects/{project_pk}/issues/{pk}/       # Issue detail
PATCH  /api/v1/projects/{project_pk}/issues/{pk}/       # Update (status, assignment)
POST   /api/v1/projects/{project_pk}/issues/{pk}/resolve/ # Mark resolved
POST   /api/v1/projects/{project_pk}/issues/{pk}/reopen/  # Reopen
POST   /api/v1/projects/{project_pk}/issues/{pk}/regression/ # Mark regression
POST   /api/v1/projects/{project_pk}/issues/{pk}/assign/   # Assign to user
GET    /api/v1/projects/{project_pk}/error-events/      # List error events

# ML (Phase 6)
GET    /api/v1/projects/{project_pk}/ml/models/         # List models
POST   /api/v1/projects/{project_pk}/ml/models/         # Create model record
GET    /api/v1/projects/{project_pk}/ml/models/{pk}/    # Model detail
POST   /api/v1/projects/{project_pk}/ml/models/{pk}/activate/ # Activate model
POST   /api/v1/projects/{project_pk}/ml/models/retrain/ # Retrain models
GET    /api/v1/projects/{project_pk}/ml/models/active/  # Get active models
GET    /api/v1/projects/{project_pk}/ml/predictions/    # List predictions
POST   /api/v1/projects/{project_pk}/ml/predictions/{pk}/feedback/ # Submit feedback
GET    /api/v1/projects/{project_pk}/ml/datasets/       # List training datasets
POST   /api/v1/projects/{project_pk}/ml/datasets/       # Create dataset
GET    /api/v1/projects/{project_pk}/ml/features/       # List feature vectors

# Dashboard (Phase 7)
GET    /api/v1/projects/{project_pk}/dashboard/overview/      # Project overview
GET    /api/v1/projects/{project_pk}/dashboard/release-detail/ # Release detail
GET    /api/v1/projects/{project_pk}/dashboard/api-health/    # API health
GET    /api/v1/projects/{project_pk}/dashboard/test-intelligence/ # Test intelligence
GET    /api/v1/projects/{project_pk}/dashboard/issues/        # Issues dashboard
GET    /api/v1/projects/{project_pk}/dashboard/summary/       # Project summary
GET    /api/v1/projects/{project_pk}/dashboard/views/         # Saved dashboard views
POST   /api/v1/projects/{project_pk}/dashboard/views/         # Create view
GET    /api/v1/projects/{project_pk}/dashboard/widgets/       # Widget configs
POST   /api/v1/projects/{project_pk}/dashboard/widgets/       # Create widget
GET    /api/v1/projects/{project_pk}/dashboard/preferences/   # User preferences

# Health & info
GET    /api/v1/health/                                   # Health check
GET    /api/v1/                                          # API root
```

**Authentication:**
- **User (dashboard)**: Session auth (Django admin/login)
- **CI/CD (ingestion)**: Project token via `Authorization: Token <token>`

---

## Development

### Running Tests
```bash
pytest                          # All tests (97 tests)
pytest apps/accounts/tests/     # Specific app
pytest -xvs                     # Verbose, stop on first failure
```

### Code Quality
```bash
ruff check .                    # Lint
ruff format .                   # Format
mypy .                          # Type check (when configured)
```

### Database
```bash
python manage.py makemigrations  # Create migrations
python manage.py migrate         # Apply migrations
python manage.py showmigrations  # Show status
python manage.py dbshell         # Direct DB access
```

### Shell
```bash
python manage.py shell           # Django shell
python manage.py shell_plus      # Enhanced shell (with shell_plus installed)
```

### Background Worker
```bash
python manage.py runworker              # Run continuously
python manage.py runworker --once       # Single cycle (testing)
python manage.py runworker --recover-stale  # Recover stuck jobs
```

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — System design, data flow, decisions
- [Decisions](docs/DECISIONS.md) — Architecture Decision Records (ADRs)
- [Learning Notes](docs/LEARNING_NOTES.md) — Concepts taught during development

---

## Demo Application: ShopAPI

A controlled demo e-commerce application with **6 deliberate regressions** for ReleaseGuard testing:

| # | Regression | Endpoint | Description |
|---|------------|----------|-------------|
| 1 | **Incorrect Calculation** | `/api/regressions/calculate-total/` | Tax on full subtotal instead of (subtotal - discount) |
| 2 | **Broken Endpoint** | `/api/regressions/broken-endpoint/` | Missing import causes `NameError` |
| 3 | **Slow Query (N+1)** | `/api/regressions/slow-products/` | Missing `select_related('category')` |
| 4 | **Unavailable Dependency** | `/api/regressions/external-payment/` | 10% chance of 503 |
| 5 | **Intermittent Failures** | `/api/regressions/flaky-checkout/` | 15% random failures |
| 6 | **Memory Heavy** | `/api/regressions/heavy-report/` | Loads entire report in memory |

**Location:** `shopapi_project/` — includes GitHub Actions workflow for ReleaseGuard integration.

---

## Deployment (Phase 8)

### Docker
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Compose Services
- **db**: PostgreSQL 16
- **redis**: Redis 7 (for future Celery)
- **app**: ReleaseGuard Django app (gunicorn in prod)
- **worker**: Background worker (`runworker`)

### Environment Variables (Production)
```bash
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgres://user:pass@db:5432/releaseguard
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
POSTGRES_PASSWORD=secure-password
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

### CI/CD (GitHub Actions)
- `.github/workflows/ci.yml` — Lint, type-check, test, migration check, Docker build
- Runs on push/PR to main/develop
- ReleaseGuard integration ready (add `RELEASEGUARD_TOKEN` and `RELEASEGUARD_PROJECT_ID` secrets)

---

## CI/CD (Phase 8)

### GitHub Actions Workflow
- **Lint & Type Check**: `ruff check .`, `ruff format --check .`, `mypy apps/`
- **Tests**: `pytest apps/` (97 tests)
- **Migrations**: `makemigrations --check`, `migrate`
- **Docker Build**: Multi-stage build, test image
- **ReleaseGuard**: Ready for integration (add secrets)

### ShopAPI Demo CI
- Runs tests, submits JUnit XML to ReleaseGuard
- Demonstrates ReleaseGuard integration for pilot

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — System design, data flow, decisions
- [Decisions](docs/DECISIONS.md) — 16 Architecture Decision Records (ADRs)
- [Learning Notes](docs/LEARNING_NOTES.md) — Concepts taught during development
- [ShopAPI Demo](shopapi_project/README.md) — Demo app with regressions

---

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Project skeleton, core models, auth | ✅ Complete |
| 2 | Release registration, JUnit XML ingestion | ✅ Complete |
| 3 | Test comparison, deterministic release policy | ✅ Complete |
| 4 | API health checks, background worker | ✅ Complete |
| 5 | Error fingerprinting, issue grouping | ✅ Complete |
| 6 | ML experiments (anomaly detection, clustering, classification) | ✅ Complete |
| 7 | Dashboard completion (overview, release, API health, test intelligence, issues) | ✅ Complete |
| 8 | Hardening, CI/CD, deployment, pilot | ✅ Complete |

---

## License

MIT License — see LICENSE file for details.