# ShopAPI Demo Application

A controlled demo application for ReleaseGuard testing with deliberate regressions.

## Overview

ShopAPI is a demo e-commerce application designed to test ReleaseGuard's regression detection capabilities. It contains **six deliberate regressions** that ReleaseGuard should be able to identify:

## Deliberate Regressions

| # | Regression | Endpoint | Description |
|---|------------|----------|-------------|
| 1 | **Incorrect Calculation** | `/api/regressions/calculate-total/` | Tax calculated on full subtotal instead of (subtotal - discount) |
| 2 | **Broken Endpoint** | `/api/regressions/broken-endpoint/` | Missing import causes `NameError` |
| 3 | **Slow Query (N+1)** | `/api/regressions/slow-products/` | Missing `select_related('category')` causes N+1 queries |
| 4 | **Unavailable Dependency** | `/api/regressions/external-payment/` | 10% chance of 503 simulating external service failure |
| 5 | **Intermittent Failures** | `/api/regressions/flaky-checkout/` | 15% random failures (timeout, 500, validation error) |
| 6 | **Memory Heavy** | `/api/regressions/heavy-report/` | Loads entire report in memory instead of streaming |

## Correct Implementations (for comparison)

| Endpoint | Description |
|----------|-------------|
| `/api/correct/calculate-total/` | Correct tax calculation on (subtotal - discount) |
| `/api/correct/fast-products/` | Uses `select_related('category')` to avoid N+1 |
| `/api/correct/streaming-report/` | Uses `StreamingHttpResponse` for memory efficiency |

## Class-Based Views

| Endpoint | Description |
|----------|-------------|
| `/api/products/` | Product list with optional `?buggy=true` for N+1 |
| `/api/checkout/` | Checkout with 20% random failure rate |

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=shop

# Run specific regression tests
pytest shop/tests/test_regressions.py -v
```

## ReleaseGuard Integration

This demo app is designed to work with ReleaseGuard:

1. **Configure ReleaseGuard token** in GitHub Actions secrets:
   - `RELEASEGUARD_TOKEN` - Project ingestion token
   - `RELEASEGUARD_PROJECT_ID` - Project UUID

2. **GitHub Actions workflow** (`.github/workflows/ci.yml`) automatically:
   - Runs tests
   - Submits JUnit XML to ReleaseGuard
   - Reports regressions detected

3. **JUnit XML output** from pytest is automatically sent to ReleaseGuard for analysis.

## Regression Detection Expected

When ReleaseGuard analyzes this demo app, it should detect:

| Regression | Detection Method | Expected Status |
|------------|------------------|-----------------|
| Incorrect Calculation | Test comparison shows different tax calculation | RED |
| Broken Endpoint | Test fails with NameError | RED |
| N+1 Query | Query count increases with products | YELLOW (performance) |
| External Dependency | 10% 503 rate detected | YELLOW (reliability) |
| Flaky Checkout | 15% random failure rate | YELLOW (flakiness) |
| Memory Heavy | Memory usage spikes on large reports | YELLOW (resource) |

## Running with ReleaseGuard

```bash
# Generate JUnit XML from tests
pytest --junitxml=results.xml

# Submit to ReleaseGuard (if CLI available)
releaseguard upload \
  --token YOUR_TOKEN \
  --project-id YOUR_PROJECT_ID \
  --junit results.xml \
  --commit $(git rev-parse HEAD) \
  --branch main
```

## Demo Data

The app includes fixture data for testing:
- Categories: Electronics, Clothing, Books, Home
- Products: Sample products in each category
- Users: Demo user accounts

Run `python manage.py loaddata demo_data.json` (if fixture exists) or use the admin to create sample data.