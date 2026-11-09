"""
Custom User model for ReleaseGuard.

Uses email as the unique identifier (USERNAME_FIELD) instead of username.
Inherits full UUID + timestamp + soft delete base.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDTimeStampedSoftDeleteModel


class UserManager(BaseUserManager):
    """
    Custom manager for User model.

    Provides create_user and create_superuser using email as the identifier.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(UUIDTimeStampedSoftDeleteModel, AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for ReleaseGuard.

    - Email is the unique identifier (USERNAME_FIELD)
    - No username field
    - Full name stored as single field (can split later if needed)
    - Soft delete supported via base class
    - UUID primary key
    """

    email = models.EmailField(_('email address'), unique=True, db_index=True)
    full_name = models.CharField(_('full name'), max_length=255, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # Use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the full name, or email if not set."""
        return self.full_name or self.email

    def get_short_name(self):
        """Return first name if available, otherwise email prefix."""
        if self.full_name:
            return self.full_name.split()[0]
        return self.email.split('@')[0]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)