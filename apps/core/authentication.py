"""
Authentication classes for ReleaseGuard.
"""

import sys
from django.conf import settings
from rest_framework.authentication import BaseAuthentication


class DevelopmentAuthentication(BaseAuthentication):
    """
    In development mode (DEBUG=True), authenticate unauthenticated requests
    as the primary admin/superuser if no other credentials are provided.
    This enables the SPA frontend to work seamlessly during development without a separate login flow.
    Always disabled during tests.
    """

    def authenticate(self, request):
        if not getattr(settings, 'DEBUG', False) or 'pytest' in sys.modules or 'test' in sys.argv:
            return None

        try:
            from apps.accounts.models import User
            admin_user = User.objects.filter(is_superuser=True, is_active=True).first()
            if admin_user:
                return (admin_user, None)
        except Exception:
            return None

        return None
