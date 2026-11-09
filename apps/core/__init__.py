"""
Core app for ReleaseGuard.

Exports base models, exceptions, and permissions.
"""

# Import exceptions and permissions (safe at module level)
from apps.core.exceptions import custom_exception_handler
from apps.core.permissions import (
    IsAuthenticated,
    IsOrganisationMember,
    IsOrganisationOwnerOrAdmin,
    IsProjectMember,
    IsProjectAdmin,
    IsTokenAuthenticated,
    CanManageReleases,
)

# Models are imported lazily to avoid AppRegistryNotReady
def get_models():
    from apps.core.models import (
        TimeStampedModel,
        UUIDModel,
        UUIDTimeStampedModel,
        SoftDeleteModel,
        UUIDTimeStampedSoftDeleteModel,
        BackgroundJob,
    )
    return {
        'TimeStampedModel': TimeStampedModel,
        'UUIDModel': UUIDModel,
        'UUIDTimeStampedModel': UUIDTimeStampedModel,
        'SoftDeleteModel': SoftDeleteModel,
        'UUIDTimeStampedSoftDeleteModel': UUIDTimeStampedSoftDeleteModel,
        'BackgroundJob': BackgroundJob,
    }

__all__ = [
    'custom_exception_handler',
    'IsAuthenticated',
    'IsOrganisationMember',
    'IsOrganisationOwnerOrAdmin',
    'IsProjectMember',
    'IsProjectAdmin',
    'IsTokenAuthenticated',
    'CanManageReleases',
    'get_models',
    'BackgroundJob',
]