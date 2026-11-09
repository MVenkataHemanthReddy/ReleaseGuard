# ReleaseGuard — Learning Notes

This document captures concepts, patterns, and explanations encountered during development. Updated each phase.

---

## Phase 1: Project Setup & Core Models

### Django Project Structure

```
releaseguard/          # Project package (settings, urls, wsgi)
apps/                  # Domain apps (each is a Python package)
  core/                # Shared base classes, exceptions, permissions
  accounts/            # Custom User model, authentication
  organizations/       # Organisation, Membership
  projects/            # Project, Environment, ProjectToken
```

**Why `apps/` subdirectory?**
- Keeps domain apps separate from project config
- Clear import paths: `from apps.core.models import ...`
- Avoids name clashes with third-party packages

### Settings with `django-environ`

```python
import environ
env = environ.Env(DEBUG=(bool, False), ...)
environ.Env.read_env(BASE_DIR / '.env')
SECRET_KEY = env('SECRET_KEY')
DATABASES = {'default': env.db('DATABASE_URL')}
```

**Key concepts:**
- **Type casting**: `env.bool()`, `env.list()`, `env.db()` parse strings to Python types
- **`.env` file**: Local development only, never committed
- **`DATABASE_URL`**: Single string → full Django DB config dict
- **12-factor config**: Environment variables for all config, no hardcoded values

### Custom User Model — Critical Timing

```python
# settings.py — MUST be before first migration
AUTH_USER_MODEL = 'accounts.User'
```

**Why before migrations?**
- Django creates `auth_user` table on first migrate
- Changing `AUTH_USER_MODEL` after requires complex data migration
- References use `settings.AUTH_USER_MODEL` (string), not direct import

**Our User model:**
```python
class User(UUIDTimeStampedSoftDeleteModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'  # Email instead of username
    objects = UserManager()   # Custom manager with create_user/create_superuser
```

### Base Model Inheritance Chain

```
TimeStampedModel          → created_at, updated_at
UUIDModel                 → id (UUID PK)
    ↓
UUIDTimeStampedModel      → id + created_at + updated_at
    ↓
SoftDeleteModel           → deleted_at + custom manager
    ↓
UUIDTimeStampedSoftDeleteModel  → Full stack (used by all domain models)
```

**Multiple inheritance order matters:**
- `UUIDTimeStampedSoftDeleteModel(UUIDTimeStampedModel, SoftDeleteModel)`
- Python MRO resolves fields correctly
- `abstract = True` on all base classes — no tables created for them

### Soft Delete Pattern

```python
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = SoftDeleteManager()      # Default: excludes deleted
    all_objects = models.Manager()     # Access all including deleted

    def delete(self, ...):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])
```

**Usage:**
```python
Project.objects.all()           # Only active projects
Project.all_objects.all()       # Includes soft-deleted
project.delete()                # Soft delete
project.hard_delete()           # Actually delete (rare)
project.restore()               # Undelete
```

**Why soft delete?**
- Audit trail / compliance
- Accidental delete recovery
- Foreign keys remain valid
- `deleted_at` index keeps queries fast

### UUID Primary Keys

```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
    db_index=True,
)
```

**Benefits:**
- Non-guessable URLs: `/api/v1/projects/550e8400-e29b-41d4-a716-446655440000/`
- No enumeration attacks
- Works across distributed systems
- No coordination needed for ID generation

**Trade-offs:**
- 16 bytes vs 8 bytes (BigAutoField)
- Not sortable by creation order (use `created_at`)
- Slightly larger indexes

### Organisation-Scoped Multi-Tenancy

```python
# Membership links User ↔ Organisation
class Membership(UUIDTimeStampedSoftDeleteModel):
    user = FK(User)
    organisation = FK(Organisation)
    role = ChoiceField(OWNER/ADMIN/MEMBER/VIEWER)
    unique_together = ('user', 'organisation')
```

**Permission enforcement:**
```python
# Every query scoped by membership
Project.objects.filter(organisation__memberships__user=request.user)
```

**Key principle**: **A UUID is not an authorisation check.** Always verify membership.

### Project Token Security

```python
class ProjectToken(UUIDTimeStampedSoftDeleteModel):
    token_hash = CharField(max_length=64)  # SHA-256 hex
    token_prefix = CharField(max_length=8)  # First 8 chars for ID

    @classmethod
    def hash_token(cls, token):
        return hashlib.sha256(token.encode()).hexdigest()

    def verify_token(self, token):
        return secrets.compare_digest(self.token_hash, self.hash_token(token))
```

**Security practices:**
- Store **only hash** (SHA-256), never plain token
- `secrets.compare_digest()` — constant-time comparison
- Prefix (`rg_abc123...`) shown in admin for identification
- Expiry + revocation (`is_active`) supported
- One-time display on creation

### Django AppConfig

```python
# apps/core/apps.py
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
```

**Why explicit AppConfig?**
- `default_auto_field` sets PK type for models in this app
- `name` must match Python import path (`apps.core`)
- `verbose_name` shows in admin
- Registered in `INSTALLED_APPS` as `'apps.core'`

### Migrations

```bash
python manage.py makemigrations  # Creates migration files
python manage.py migrate         # Applies to database
```

**Migration files are:**
- Version control for schema
- Python files with `operations = [...]`
- Reversible (usually)
- Run in dependency order

**First migration creates:**
- All tables for new models
- Indexes from `db_index=True` and `Meta.indexes`
- Constraints from `UniqueConstraint`, `CheckConstraint`

### Admin Customization

```python
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'is_active', ...)
    fieldsets = (...)  # Edit form layout
    add_fieldsets = (...)  # Create form layout
```

**Key points:**
- Extend `BaseUserAdmin` for custom User model
- `readonly_fields` for auto-populated fields (id, timestamps)
- `raw_id_fields` for FK to large tables (avoids huge dropdowns)
- `prepopulated_fields` for slug from name

### Management Commands

```bash
python manage.py createsuperuser --email admin@... --full_name "Admin"
python manage.py shell -c "..."  # Run Django shell command
```

### Runserver

```bash
python manage.py runserver 0.0.0.0:8000
```
- `0.0.0.0` binds to all interfaces (accessible from network)
- Auto-reloads on code changes
- Serves static files in DEBUG mode

---

## Concepts to Remember

| Concept | Key Takeaway |
|---------|--------------|
| `AUTH_USER_MODEL` | Set **before first migration** |
| Base model inheritance | Order matters; all `abstract = True` |
| Soft delete | `objects` filters, `all_objects` includes all |
| UUID PK | Non-guessable, safe for public URLs |
| Multi-tenancy | Every query scoped by membership |
| Token security | Hash only, constant-time compare |
| `django-environ` | Type-safe env parsing, `.env` for dev |
| AppConfig | Explicit config per app, `name` = import path |

---

## Next Phase Preview (Phase 2)

- Release registration endpoint
- JUnit XML upload + parsing
- Idempotency keys
- Transactional storage
- Background job for async processing

---

## Phase 2: Release Registration & JUnit XML Ingestion

### Safe JUnit XML Parsing with `defusedxml`

```python
from defusedxml import ElementTree as ET
from defusedxml.common import EntitiesForbidden

# Parse with protection against:
# - DTD/Entity expansion (billion laughs)
# - External entity references (XXE)
# - EntityForbidden exceptions

try:
    root = ET.fromstring(xml_content)
except EntitiesForbidden:
    raise JUnitParserError('XML contains forbidden entity references')
```

**Why defusedxml?**
- Standard `xml.etree.ElementTree` is vulnerable to XML bombs
- `defusedxml` blocks DTD, external entities, entity expansion
- Drop-in replacement for stdlib ElementTree API

### JUnit XML Structure

```xml
<testsuites>              <!-- Root for multiple suites -->
  <testsuite name="unit">  <!-- Single test suite -->
    <properties>           <!-- Suite-level metadata -->
      <property name="os" value="linux"/>
    </properties>
    <testcase classname="test_math" name="test_add" time="0.1">
      <failure message="AssertionError">traceback</failure>
      <system-out>stdout</system-out>
      <system-err>stderr</system-err>
      <properties>         <!-- Test-case metadata -->
        <property name="xfail" value="true"/>
      </properties>
    </testcase>
  </testsuite>
</testsuites>
```

**Key elements parsed:**
- `testsuite`: name, tests, failures, errors, skipped, time, timestamp, hostname
- `testcase`: classname, name, time, status (passed/failed/skipped/error/xfail/xpass)
- `failure`/`error`/`skipped`: message attribute + text content (traceback)
- `system-out`/`system-err`: stdout/stderr capture
- `properties`: key-value metadata at both suite and testcase level

### Idempotency Keys for CI/CD Retries

```python
# GitHub Actions provides unique workflow_run_id per run
# Even on retry, the same workflow_run_id is used
idempotency_key = f'{workflow_run_id}:{test_suite_name}'

# In TestRun model:
class TestRun(UUIDTimeStampedSoftDeleteModel):
    idempotency_key = models.CharField(max_length=255, db_index=True)
    # Unique constraint: (release, idempotency_key)

# Get or create pattern:
test_run, created = TestRun.objects.get_or_create(
    release=release,
    idempotency_key=idempotency_key,
    defaults={'name': test_run_name, 'status': 'processing'}
)
```

**Why idempotency matters:**
- CI/CD retries send same data multiple times
- Without idempotency: duplicate test runs, inflated counts
- With idempotency: safe to retry, updates existing record

### Background Job Queue (PostgreSQL-backed)

```python
class BackgroundJob(UUIDTimeStampedModel):
    name = models.CharField(max_length=255)  # e.g., 'generate_release_analysis'
    status = ChoiceField(PENDING/CLAIMED/RUNNING/COMPLETED/FAILED/DEAD)
    priority = IntegerField(choices=LOW/NORMAL/HIGH/CRITICAL)
    payload = JSONField()      # Input data
    result = JSONField()       # Output data
    error = TextField()        # Error message
    max_retries = 3
    retry_count = 0
    scheduled_at = DateTimeField()
    idempotency_key = CharField()  # Prevent duplicate jobs
```

**Job claiming (atomic, concurrent-safe):**
```python
# PostgreSQL: SELECT FOR UPDATE SKIP LOCKED
job = queryset.select_for_update(skip_locked=True).first()

# SQLite fallback: atomic UPDATE
updated = Model.objects.filter(pk=job.pk, status=PENDING).update(
    status=CLAIMED, worker_id=worker_id
)
```

**Worker loop:**
```python
while running:
    job = BackgroundJob.claim_next_job(worker_id)
    if job:
        try:
            process_job(job)
            job.mark_completed(result)
        except Exception as e:
            job.mark_failed(str(e), will_retry=job.can_retry())
    time.sleep(poll_interval)
```

**Features:**
- Zero external dependencies (no Redis/Celery)
- Transactional claiming (no lost jobs)
- Retry with exponential backoff
- Stale job recovery (crashed workers)
- Idempotency keys prevent duplicates

### Release Comparison Logic

```python
# Compare current vs previous release test results
# Categorize each test:
# - New failure: failed now, passed/absent before
# - Persistent failure: failed in both
# - Fixed failure: failed before, passes now
# - Unchanged passing: passed in both

current_map = {tc.test_identifier: tc for tc in current_results}
previous_map = {tc.test_identifier: tc for tc in previous_results}

for identifier in all_identifiers:
    current = current_map.get(identifier)
    previous = previous_map.get(identifier)
    
    if current_failed and not previous_failed:
        new_failures.append(current)
    elif current_failed and previous_failed:
        persistent_failures.append(current)
    elif not current_failed and previous_failed and current_passed:
        fixed_failures.append(previous)  # Show what was fixed
    elif current_passed and previous_passed:
        unchanged_passing.append(current)
```

### Deterministic Policy Engine

```python
# Rules evaluated in order, each has severity:
# - blocking -> RED if failed
# - warning -> YELLOW if failed (but no blocking failures)

RULES = [
    {'id': 'required_tests_pass', 'severity': 'blocking'},
    {'id': 'no_new_failures', 'severity': 'blocking'},
    {'id': 'critical_health_checks', 'severity': 'blocking'},
    {'id': 'no_persistent_failures', 'severity': 'warning'},
    {'id': 'flaky_test_threshold', 'severity': 'warning'},
    {'id': 'test_duration_anomaly', 'severity': 'warning'},
]

# Overall status:
# RED if ANY blocking rule fails
# YELLOW if NO blocking failures but ANY warning rule fails
# GREEN if all pass
```

**Key principle:** ML is advisory only; deterministic rules decide GREEN/YELLOW/RED.

### DRF ViewSets with Project Scoping

```python
class ProjectScopedViewSetMixin:
    def get_project(self):
        project = get_object_or_404(Project, pk=project_pk)
        # Verify membership
        if not user.memberships.filter(organisation=project.organisation).exists():
            self.permission_denied(request)
        return project

    def get_queryset(self):
        project = self.get_project()
        return Model.objects.filter(project=project)
```

**Permission classes:**
- `IsProjectMember`: Any active role in project's organisation
- `IsProjectAdmin`: OWNER/ADMIN/MEMBER (write), VIEWER (read-only)
- `CanManageReleases`: For ingestion endpoints

### Test Fingerprinting for Error Grouping

```python
def generate_test_fingerprint(classname, name, traceback):
    # Normalize traceback: remove paths, line numbers, variable values
    normalized_tb = normalize_traceback(traceback)
    source = f'{classname}.{name}|{normalized_tb}'
    return hashlib.sha256(source.encode()).hexdigest()[:32]

def normalize_traceback(tb):
    # Remove file paths: /path/to/file.py:123 -> file.py
    # Remove line numbers
    # Remove memory addresses: 0x7f8b... -> 0x...
    # Normalize string values: "value" -> "..."
    # Normalize numbers: = 42 -> = N
```

---

## Concepts to Remember (Phase 2)

| Concept | Key Takeaway |
|---------|--------------|
| `defusedxml` | Always use for untrusted XML input |
| Idempotency key | `workflow_run_id:suite_name` for CI retries |
| BackgroundJob | PostgreSQL table + worker command, no Redis |
| Release comparison | Set operations on test identifiers |
| Policy engine | Blocking rules -> RED, Warning rules -> YELLOW |
| Fingerprinting | Normalize traceback before hashing |
| Project scoping | Every query filtered by membership |