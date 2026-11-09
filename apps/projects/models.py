"""
Project, Environment, and ProjectToken models for ReleaseGuard.

Projects belong to Organisations.
Environments belong to Projects (e.g., staging, production).
ProjectTokens are used for CI/CD ingestion (machine auth).
"""

import hashlib
import secrets
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDTimeStampedSoftDeleteModel


class Project(UUIDTimeStampedSoftDeleteModel):
    """
    A software project within an organisation.

    Each project has its own environments, tokens, releases, and data.
    Scoped to organisation for multi-tenancy.
    """

    organisation = models.ForeignKey(
        'organizations.Organisation',
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name=_('organisation'),
    )
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=100, db_index=True)
    description = models.TextField(_('description'), blank=True)
    repository_url = models.URLField(_('repository URL'), blank=True)
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['organisation', 'slug'],
                name='unique_project_slug_per_organisation',
            ),
        ]
        indexes = [
            models.Index(fields=['organisation', 'slug', 'is_active']),
        ]

    def __str__(self):
        return f'{self.organisation.name} / {self.name}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('projects:detail', kwargs={'pk': self.pk})


class Environment(UUIDTimeStampedSoftDeleteModel):
    """
    Deployment environment for a project (e.g., staging, production, preview).

    Used to scope releases and API health checks to specific environments.
    """

    class Type(models.TextChoices):
        DEVELOPMENT = 'development', _('Development')
        STAGING = 'staging', _('Staging')
        PRODUCTION = 'production', _('Production')
        PREVIEW = 'preview', _('Preview')
        TESTING = 'testing', _('Testing')
        OTHER = 'other', _('Other')

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='environments',
        verbose_name=_('project'),
    )
    name = models.CharField(_('name'), max_length=100)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=Type.choices,
        default=Type.STAGING,
        db_index=True,
    )
    description = models.TextField(_('description'), blank=True)
    base_url = models.URLField(_('base URL'), blank=True, help_text=_('Base URL for API health checks'))
    is_active = models.BooleanField(_('active'), default=True)
    is_default = models.BooleanField(_('default'), default=False)

    class Meta:
        verbose_name = _('environment')
        verbose_name_plural = _('environments')
        ordering = ['type', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'name'],
                name='unique_environment_name_per_project',
            ),
            models.UniqueConstraint(
                fields=['project', 'is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_environment_per_project',
            ),
        ]
        indexes = [
            models.Index(fields=['project', 'type', 'is_active']),
        ]

    def __str__(self):
        return f'{self.project.name} / {self.name}'

    def save(self, *args, **kwargs):
        # Ensure only one default environment per project
        if self.is_default:
            Environment.objects.filter(project=self.project, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class ProjectToken(UUIDTimeStampedSoftDeleteModel):
    """
    Machine authentication token for CI/CD ingestion.

    - Scoped to a single project
    - Stores only SHA-256 hash (never plain token)
    - Supports revocation and expiry
    - Used for test report uploads, release registration
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name=_('project'),
    )
    name = models.CharField(_('name'), max_length=255, help_text=_('Human-readable name, e.g., "GitHub Actions - main"'))
    token_hash = models.CharField(_('token hash'), max_length=64, unique=True, db_index=True)
    token_prefix = models.CharField(_('token prefix'), max_length=8, db_index=True, help_text=_('First 8 chars for identification'))
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    expires_at = models.DateTimeField(_('expires at'), null=True, blank=True, db_index=True)
    last_used_at = models.DateTimeField(_('last used at'), null=True, blank=True)

    class Meta:
        verbose_name = _('project token')
        verbose_name_plural = _('project tokens')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'is_active', 'expires_at']),
        ]

    def __str__(self):
        return f'{self.project.name} / {self.name} ({self.token_prefix}...)'

    @classmethod
    def generate_token(cls):
        """Generate a new random token (32 bytes = 256 bits)."""
        return secrets.token_urlsafe(32)

    @classmethod
    def hash_token(cls, token: str) -> str:
        """Return SHA-256 hex digest of token."""
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def create_token(cls, project, name, description='', expires_at=None):
        """
        Create a new token and return (token_instance, plain_token).

        The plain token is ONLY returned once — store it immediately.
        """
        plain_token = cls.generate_token()
        token_hash = cls.hash_token(plain_token)
        token_prefix = plain_token[:8]

        token = cls.objects.create(
            project=project,
            name=name,
            description=description,
            token_hash=token_hash,
            token_prefix=token_prefix,
            expires_at=expires_at,
        )
        return token, plain_token

    def verify_token(self, token: str) -> bool:
        """Verify a plain token against stored hash (constant-time)."""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return secrets.compare_digest(self.token_hash, self.hash_token(token))

    def record_usage(self):
        """Update last_used_at timestamp."""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])