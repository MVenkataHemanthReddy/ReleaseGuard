# ReleaseGuard Dockerfile
# Multi-stage build for production

# ---- Base Stage ----
FROM python:3.12-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r releaseguard && useradd -r -g releaseguard releaseguard

# Set work directory
WORKDIR /app

# ---- Dependencies Stage ----
FROM base as dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Development Stage ----
FROM dependencies as development

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
RUN chown -R releaseguard:releaseguard /app

USER releaseguard

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ---- Production Stage ----
FROM dependencies as production

# Copy application code
COPY --chown=releaseguard:releaseguard . .

# Collect static files
RUN python manage.py collectstatic --noinput --clear

USER releaseguard

EXPOSE 8000

# Use gunicorn for production
CMD ["gunicorn", "releaseguard.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]