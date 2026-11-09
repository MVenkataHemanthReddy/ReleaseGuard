"""
Custom exception handler for ReleaseGuard API.

Provides consistent error response format across all API endpoints.
"""

import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that wraps DRF's default handler.

    Returns consistent error format:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "details": {}  # optional field-specific errors
        }
    }
    """
    # Call DRF's default exception handler first
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Standardize the response format
        custom_response = {
            'error': {
                'code': getattr(exc, 'default_code', 'error'),
                'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
                'details': getattr(exc, 'detail', None) if isinstance(getattr(exc, 'detail', None), dict) else None,
            }
        }
        response.data = custom_response
        return response

    # Unhandled exception (500)
    logger.exception('Unhandled exception in API', exc_info=exc)
    return Response(
        {
            'error': {
                'code': 'internal_server_error',
                'message': 'An unexpected error occurred. Please try again later.',
                'details': None,
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )