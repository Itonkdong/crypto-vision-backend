from rest_framework.views import exception_handler
from rest_framework.response import Response
from .auth_exceptions import AccountLockedException, LoginFailedException


def custom_auth_exception_handler(exc, context):
    """Custom exception handler for authentication exceptions"""
    response = exception_handler(exc, context)

    if isinstance(exc, AccountLockedException):
        custom_response_data = {
            'success': False,
            'error': str(exc.detail),
            'locked': True,
            'remaining_time': getattr(exc, 'remaining_time', 0)
        }
        response.data = custom_response_data

    elif isinstance(exc, LoginFailedException):
        custom_response_data = {
            'success': False,
            'error': str(exc.detail),
            'remaining_attempts': getattr(exc, 'remaining_attempts', 0)
        }
        response.data = custom_response_data

    return response
