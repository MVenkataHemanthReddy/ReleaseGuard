# ReleaseGuard Architecture

## Overview

ReleaseGuard is a **modular monolith** built with Django + DRF, using PostgreSQL as the primary datastore. A separate background worker process handles asynchronous jobs using a PostgreSQL-backed job queue.

```
┌─────────────────────────────────────────────────────────────┐
│                     ReleaseGuard Monolith                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Accounts │  │Organisations│  │ Projects │  │   Core     │  │
│  │   App    │  │   App    │  │   App    │  │   App      │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│         │           │           │           │               │
│         └───────────┴───────────┴───────────┘               │
│                         │                                   │
│              ┌──────────▼──────────┐                         │
│              │   Shared Models     │                         │
│              │  (UUID, timestamps, │                         │
│              │   soft delete)      │                         │
│              └──────────┬──────────┘                         │
│                         │                                   │
│              ┌──────────▼──────────┐                         │
│              │   PostgreSQL        │                         │
│              │   (single DB)       │                         │
│              └─────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Background Worker │  (separate process)
                    │  (management cmd) │
                    └───────────────────┘
```

## Domain Model

```
Organisation (tenant)
    │
    ├── Membership (User ↔ Organisation, role: OWNER/ADMIN/MEMBER/VIEWER)
    │
    └── Project
            │
            ├── Environment (development/staging/production/preview)
            │
            ├── ProjectToken (machine auth for CI/CD)
            │
            ├── Release
            │     │
            │     ├── TestRun
            │     │     └── TestCaseResult
            │     │
            │     ├── ReleaseAnalysis (policy result: GREEN/YELLOW/RED)
            │     │
            │     └── ErrorEvent → IssueGroup
            │
            ├── ApiCheck
            │     └── ApiCheckResult
            │
            └── BackgroundJob
```

## Key Design Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Architecture** | Modular monolith | Simplicity, single deployable, clear module boundaries |
| **Database** | Single PostgreSQL | ACID transactions across domains, no distributed complexity |
| **Auth** | Custom User (email) + Session + Token | Django-native, email-based login, machine tokens for CI |
| **Multi-tenancy** | Organisation-scoped queries | Row-level security via foreign keys, not RLS |
| **Soft deletes** | `deleted_at` + custom manager | Audit trail, recoverability, no data loss |
| **Primary keys** | UUID (v4) | Non-guessable, safe for public URLs, no enumeration |
| **Background jobs** | PostgreSQL table + management command | No Redis/Celery dependency, transactional, recoverable |
| **Frontend** | Django templates + vanilla JS | Single deployable, no build step, progressive enhancement |
| **API** | DRF with `/api/v1/` | Versioned, standard REST, token + session auth |

## Data Flow: CI/CD Ingestion

```
GitHub Actions (CI)
       │
       ▼
Pytest → JUnit XML
       │
       ▼
ReleaseGuard Uploader (small CLI)
       │
       ▼
POST /api/v1/projects/{id}/releases/     → Release registration
POST /api/v1/releases/{id}/test-runs/    → JUnit XML upload
       │
       ▼
Background Job (async processing)
       │
       ├── Parse & validate XML
       ├── Store TestRun + TestCaseResults
       ├── Compare with previous release
       ├── Evaluate deterministic policy
       └── Create ReleaseAnalysis (GREEN/YELLOW/RED)
       │
       ▼
Dashboard shows result
```

## Security Considerations

- **SSRF Protection**: API health checks validate URLs, block private IPs, enforce timeouts
- **Token Security**: Project tokens stored as SHA-256 hashes only, constant-time comparison
- **Multi-tenancy**: Every query scoped by organisation membership (UUID ≠ auth)
- **Secrets**: `.env` for config, never committed; `.env.example` for template
- **Rate Limiting**: To be added on ingestion endpoints

## Future Extensions (Post-MVP)

- Celery + Redis if background job throughput demands it
- Separate frontend (React/Vue) if UI complexity grows
- Webhooks / GitHub App for PR comments
- ML services as separate microservices if needed