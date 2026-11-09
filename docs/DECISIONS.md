# ReleaseGuard — Architecture Decision Records (ADRs)

Each decision records the context, options considered, and the chosen path.

---

## ADR-001: Modular Monolith Architecture

**Date**: 2025-11-08
**Status**: Accepted

### Context
Need to build a release-centric reliability platform for small Python teams. Must balance simplicity with maintainability.

### Options
1. **Microservices** — Separate services for auth, projects, ingestion, analysis, dashboard
2. **Modular Monolith** — Single Django project with domain-focused apps, shared database
3. **Serverless** — Cloud functions for ingestion, managed DB

### Decision
**Modular Monolith** with Django apps: `accounts`, `organizations`, `projects`, `core`.

### Rationale
- Single deployable artifact
- ACID transactions across domain boundaries
- No network latency / distributed debugging complexity
- Clear module boundaries enforce separation
- Can extract services later if needed (not premature)

### Consequences
- All apps share one database
- Scaling is vertical (or read replicas) initially
- Deployment is simpler

---

## ADR-002: Custom User Model with Email as Username

**Date**: 2025-11-08
**Status**: Accepted

### Context
Django's default User uses username. ReleaseGuard should use email for authentication.

### Options
1. Keep default User, add email field
2. Custom User model (AbstractBaseUser) with email as USERNAME_FIELD
3. Use django-allauth or similar

### Decision
**Custom User model** (`apps.accounts.models.User`) with `USERNAME_FIELD = 'email'`.

### Rationale
- Must be done before first migration (Django requirement)
- Email is the natural identifier for SaaS
- No username field reduces confusion
- Full control over auth flow

### Consequences
- Requires `AUTH_USER_MODEL = 'accounts.User'` in settings before migrations
- Admin customization needed
- Third-party packages must reference `settings.AUTH_USER_MODEL`

---

## ADR-003: UUID Primary Keys for All Domain Models

**Date**: 2025-11-08
**Status**: Accepted

### Context
Primary key choice affects URL design, security, and database performance.

### Options
1. Auto-incrementing Integer (BigAutoField)
2. UUID v4 (random)
3. ULID / KSUID (sortable)

### Decision
**UUID v4** via `UUIDTimeStampedSoftDeleteModel` base class.

### Rationale
- Non-guessable — safe for public API URLs
- No information leakage about record counts
- Works well with distributed systems (no coordination)
- Django native support (`UUIDField`)
- Acceptable index performance with proper indexing

### Consequences
- Larger storage (16 bytes vs 8 bytes)
- Not naturally sortable by creation time (use `created_at` instead)
- Migration from int PK later is painful — decide early

---

## ADR-004: Soft Deletes via `deleted_at` Timestamp

**Date**: 2025-11-08
**Status**: Accepted

### Context
Data loss from accidental deletes is unacceptable. Audit trail required.

### Options
1. Hard delete (DELETE FROM)
2. Soft delete column (`deleted_at`) + custom manager
3. Audit log table + triggers

### Decision
**Soft delete** with `deleted_at` timestamp and `SoftDeleteManager`.

### Rationale
- Simple to implement and understand
- `Model.objects` auto-filters deleted records
- `Model.all_objects` includes deleted for admin/recovery
- Single column, indexed for performance
- `restore()` method enables undo

### Consequences
- All queries must consider `deleted_at` (handled by manager)
- Unique constraints must account for soft deletes (partial indexes)
- Storage grows over time (periodic cleanup job needed)

---

## ADR-005: PostgreSQL-Backed Background Job Queue

**Date**: 2025-11-08
**Status**: Accepted

### Context
Async processing needed for JUnit parsing, release comparison, API checks, ML.

### Options
1. Celery + Redis
2. Celery + PostgreSQL (django-celery-beat)
3. Custom PostgreSQL job table + management command worker
4. Django-Q / Huey

### Decision
**Custom PostgreSQL job table** (`BackgroundJob` model) + Django management command worker.

### Rationale
- Zero additional infrastructure (no Redis)
- Transactional job claiming with `SELECT FOR UPDATE SKIP LOCKED`
- Jobs are part of the same DB — can join with domain models
- Idempotency keys stored on job row
- Retry logic, backoff, stale job recovery all in SQL/Python
- Simple enough for MVP throughput

### Consequences
- Worker is a separate process (`python manage.py runworker`)
- Polling interval adds latency (configurable)
- Not suitable for high-throughput / low-latency needs
- Can migrate to Celery later if metrics justify it

---

## ADR-006: Django Templates + Vanilla JavaScript for Frontend

**Date**: 2025-11-08
**Status**: Accepted

### Context
Dashboard UI needed for project overview, releases, test intelligence, API health, issues.

### Options
1. Django templates + vanilla JS (progressive enhancement)
2. Separate React/Vue/Svelte SPA
3. HTMX + Django templates
4. Django Unicorn / Alpine.js

### Decision
**Django templates + vanilla JavaScript** (ES6 modules, no build step).

### Rationale
- Single deployable (no separate frontend build/deploy)
- No Node.js toolchain required
- Progressive enhancement — works without JS
- HTMX can be added later for partial updates
- Team skill alignment (Python-first)

### Consequences
- Less reactive UX than SPA
- More server-roundtrips
- Can extract to SPA later if UX demands it

---

## ADR-007: Project-Scoped Ingestion Tokens (SHA-256 Hashed)

**Date**: 2025-11-08
**Status**: Accepted

### Context
CI/CD pipelines need to authenticate to upload test reports.

### Options
1. User API keys (personal)
2. Project-scoped tokens (machine)
3. JWT with short expiry
4. GitHub App / OAuth

### Decision
**Project-scoped tokens** stored as SHA-256 hash, with prefix for identification.

### Rationale
- Scoped to project (not user) — survives team changes
- Hash-only storage — token unrecoverable if DB leaked
- Prefix (`rg_abc123...`) allows identification without full token
- Expiry and revocation supported
- Simple for CI: `curl -H "Authorization: Token <token>"`

### Consequences
- Token only shown once at creation
- No password reset equivalent — must regenerate
- Rate limiting needed on ingestion endpoints

---

## ADR-008: Deterministic Policy Engine (Not ML) for Release Status

**Date**: 2025-11-08
**Status**: Accepted

### Context
Release status (GREEN/YELLOW/RED) must be explainable and consistent.

### Options
1. ML classifier trained on historical data
2. Rule-based deterministic engine
3. Hybrid: rules + ML anomaly detection as advisory

### Decision
**Deterministic rule engine** for GREEN/YELLOW/RED. ML only as advisory layer (anomaly detection).

### Rationale
- Teams need to understand *why* a release is RED
- Rules are auditable, testable, configurable
- ML can produce false positives/negatives without explanation
- ML added later as "insight" not "decision"
- Policy version recorded for reproducibility

### Consequences
- Policy configuration in DB (JSON or structured fields)
- Rule evaluation logic in service layer (testable)
- ML features (Isolation Forest, clustering) are separate, optional

---

## ADR-009: SQLite for Development, PostgreSQL for Production

**Date**: 2025-11-08
**Status**: Accepted

### Context
Local development database choice.

### Options
1. PostgreSQL locally (native or Docker)
2. SQLite for dev, PostgreSQL for prod
3. PostgreSQL everywhere (including CI)

### Decision
**SQLite for development**, PostgreSQL for production/CI.

### Rationale
- Zero setup for new developers
- `DATABASE_URL=sqlite:///db.sqlite3` in `.env`
- Django ORM abstracts differences
- CI/CD uses PostgreSQL (GitHub Actions service container)
- `django-environ` makes switching trivial

### Consequences
- Some PostgreSQL features not available in SQLite (partial indexes, `FOR UPDATE SKIP LOCKED`)
- Worker job locking uses advisory locks as fallback in SQLite
- Must test migrations on PostgreSQL before deploy

---

## ADR-010: Environment Variables via django-environ

**Date**: 2025-11-08
**Status**: Accepted

### Context
Configuration management across dev/staging/prod.

### Options
1. `settings.py` with `os.environ.get()`
2. `python-decouple`
3. `django-environ`
4. Django's built-in `Env` (3.2+)

### Decision
**django-environ** with `.env` file for development.

### Rationale
- Type casting (`env.bool()`, `env.list()`, `env.db()`)
- `.env` file support for local dev
- `DATABASE_URL` parsing built-in
- Widely used, well-maintained
- `.env.example` documents required variables

### Consequences
- `.env` never committed (in `.gitignore`)
- Production uses actual environment variables
- Secret management via platform (GitHub Actions secrets, etc.)

---

## ADR-011: Safe JUnit XML Parsing with defusedxml

**Date**: 2025-11-08
**Status**: Accepted

### Context
CI/CD pipelines upload JUnit XML test reports. These are untrusted input from external systems.

### Options
1. Python stdlib `xml.etree.ElementTree` (vulnerable to XML bombs)
2. `defusedxml` (stdlib-compatible, blocks attacks)
3. `lxml` with custom parser settings
4. Custom XML parser

### Decision
**defusedxml** for parsing, with `lxml` as optional backend for performance.

### Rationale
- Drop-in replacement for stdlib ElementTree API
- Blocks DTD, external entities, entity expansion (billion laughs)
- Raises `EntitiesForbidden` on attack attempts
- Zero config, minimal overhead
- `lxml` backend available if needed for large files

### Consequences
- Must catch `EntitiesForbidden` and `ParseError` exceptions
- Slightly slower than raw `lxml` for huge files
- All XML input treated as untrusted

---

## ADR-012: Idempotency Keys for CI/CD Ingestion

**Date**: 2025-11-08
**Status**: Accepted

### Context
GitHub Actions (and other CI) may retry failed workflow runs, sending identical payloads multiple times.

### Options
1. No deduplication (accept duplicates)
2. Client-generated UUID per submission
3. Server-generated idempotency key from CI metadata
4. Hash of payload content

### Decision
**Server-generated idempotency key** from `workflow_run_id:test_suite_name`.

### Rationale
- GitHub Actions provides stable `workflow_run_id` per run (even on retry)
- Combining with test suite name handles multiple test suites per workflow
- Unique constraint on `(release, idempotency_key)` prevents duplicates
- No client changes needed
- Natural fit for "retry-safe" CI/CD

### Consequences
- Requires `workflow_run_id` in ingestion payload
- Different CI systems need adaptation (GitLab `CI_PIPELINE_ID`, etc.)
- Unique constraint must be at database level

---

## ADR-013: Release Comparison via Test Identifier Sets

**Date**: 2025-11-08
**Status**: Accepted

### Context
Need to compare test results between releases to identify new/persistent/fixed failures.

### Options
1. Compare by test name only (classname + method)
2. Compare by test fingerprint (includes traceback)
3. Compare by full test object equality
4. Database-level set operations

### Decision
**Compare by test identifier** (`classname.name`) using Python set operations in service layer.

### Rationale
- Test identifier is stable across runs (unlike traceback)
- Simple set operations: new = current - previous, fixed = previous - current
- Fast enough for thousands of tests
- Traceback-based fingerprinting used separately for error grouping

### Consequences
- Renamed tests appear as "new" + "fixed" pair
- Parametrized tests need unique identifiers (pytest handles this)
- Fingerprinting for error grouping is separate concern

---

## ADR-014: Deterministic Policy Engine with Blocking/Warning Rules

**Date**: 2025-11-08
**Status**: Accepted

### Context
Release status (GREEN/YELLOW/RED) must be explainable, consistent, and configurable.

### Options
1. Hardcoded logic in views
2. Configurable rules with severity levels
3. ML classifier with confidence thresholds
4. External policy engine (OPA, etc.)

### Decision
**Configurable rule list** with `severity: blocking|warning` in service layer.

### Rationale
- Rules are auditable, testable, versionable (`policy_version`)
- Blocking rules -> RED, Warning rules -> YELLOW (if no blocking failures)
- Easy to add/remove/modify rules without code changes
- Rule results stored per-release for explainability
- ML can add advisory annotations later

### Consequences
- Rule evaluation order matters for explainability
- Policy version must be recorded per analysis
- Complex rules may need custom evaluators

---

## ADR-015: Background Job Queue via PostgreSQL Table

**Date**: 2025-11-08
**Status**: Accepted

### Context
Async processing for JUnit parsing, release analysis, API checks, ML.

### Options
1. Celery + Redis (industry standard)
2. Celery + PostgreSQL (django-celery-beat)
3. Custom `BackgroundJob` model + management command worker
4. Django-Q / Huey / Dramatiq

### Decision
**Custom `BackgroundJob` model** + `runworker` management command.

### Rationale
- Zero external infrastructure (no Redis)
- Transactional job claiming with `SELECT FOR UPDATE SKIP LOCKED`
- Jobs join with domain models (same DB)
- Retry, backoff, stale recovery in pure Python/SQL
- Simple enough for MVP throughput (~100 jobs/min)

### Consequences
- Worker is separate process (`python manage.py runworker`)
- Polling latency (configurable, default 5s)
- SQLite fallback uses advisory locks (no `SKIP LOCKED`)
- Migrate to Celery when throughput/latency demands it

---

## ADR-016: Test Fingerprinting for Error Grouping

**Date**: 2025-11-08
**Status**: Accepted

### Context
Need to group similar errors across test runs/releases for issue tracking.

### Options
1. Group by exact traceback match
2. Group by exception type + test name
3. Normalized traceback hash (deterministic)
4. ML-based clustering (TF-IDF + similarity)

### Decision
**Normalized traceback SHA-256 hash** (32 chars) as primary fingerprint.

### Rationale
- Deterministic: same error -> same fingerprint
- Normalization removes noise (paths, line numbers, variable values)
- Works immediately without training data
- ML clustering (ADR future) can augment for missed groups

### Consequences
- Normalization regex must handle common traceback formats
- Different exception types with same traceback get different fingerprints (includes classname.method)
- False negatives possible if normalization too aggressive