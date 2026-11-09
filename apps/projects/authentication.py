"""
Custom authentication for ReleaseGuard.

Uses ProjectToken for machine-to-machine authentication (CI/CD).
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ProjectTokenAuthentication(BaseAuthentication):
    """
    Authenticate using ProjectToken.

    Expected header: Authorization: Token <plain_token>

    The token is verified against the stored hash in ProjectToken.
    """

    keyword = 'Token'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith(self.keyword + ' '):
            return None

        token = auth_header[len(self.keyword) + 1:].strip()

        if not token:
            return None

        # Import model lazily to avoid circular import at module load time
        from apps.projects.models import ProjectToken

        # Find matching token by prefix (first 8 chars)
        token_prefix = token[:8]
        try:
            project_token = ProjectToken.objects.select_related('project').get(
                token_prefix=token_prefix,
                is_active=True
            )
        except ProjectToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        # Verify the full token against hash
        if not project_token.verify_token(token):
            raise AuthenticationFailed('Invalid token')

        # Record usage
        project_token.record_usage()

        # Return a wrapper that acts like an authenticated user
        # We use the project as the "user" for permission checks
        project = project_token.project
        project.is_authenticated = True  # Add flag for permission checks
        project._project_token = project_token  # Store token for reference
        return (project, project_token)

    def authenticate_header(self, request):
        return self.keyword