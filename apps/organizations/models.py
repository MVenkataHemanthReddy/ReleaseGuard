"""
Organisation and Membership models for ReleaseGuard.

Organisations are the top-level tenant container.
Memberships link Users to Organisations with roles.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDTimeStampedSoftDeleteModel


class Organisation(UUIDTimeStampedSoftDeleteModel):
    """
    Top-level tenant container.

    All projects, releases, and data belong to an organisation.
    Multi-tenancy is enforced by scoping all queries to organisation.
    """

    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=100, unique=True, db_index=True)
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        verbose_name = _('organisation')
        verbose_name_plural = _('organisations')
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('organisations:detail', kwargs={'pk': self.pk})


class Membership(UUIDTimeStampedSoftDeleteModel):
    """
    Links a User to an Organisation with a specific role.

    A user can belong to multiple organisations with different roles.
    Roles determine permissions within the organisation.
    """

    class Role(models.TextChoices):
        OWNER = 'OWNER', _('Owner')
        ADMIN = 'ADMIN', _('Admin')
        MEMBER = 'MEMBER', _('Member')
        VIEWER = 'VIEWER', _('Viewer')

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('user'),
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('organisation'),
    )
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
        db_index=True,
    )
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'organisation'],
                name='unique_user_organisation_membership',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'organisation', 'is_active']),
        ]

    def __str__(self):
        return f'{self.user.email} @ {self.organisation.name} ({self.role})'

    # Permission helpers
    def can_manage_organisation(self):
        return self.role in (self.Role.OWNER, self.Role.ADMIN)

    def can_manage_projects(self):
        return self.role in (self.Role.OWNER, self.Role.ADMIN, self.Role.MEMBER)

    def can_view_only(self):
        return self.role == self.Role.VIEWER