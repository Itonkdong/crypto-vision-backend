from rest_framework import status
from rest_framework.exceptions import APIException


class AuthValidationError(APIException):
    """Base exception for authentication validation errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation error occurred.'
    default_code = 'validation_error'


class LoginValidationError(AuthValidationError):
    """Exception for login validation errors"""
    default_detail = 'Invalid login credentials.'


class AccountLockedException(APIException):
    """Exception when account is locked due to failed attempts"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Account is temporarily locked.'
    default_code = 'account_locked'

    def __init__(self, detail=None, remaining_time=None):
        super().__init__(detail)
        self.remaining_time = remaining_time


class LoginFailedException(APIException):
    """Exception for failed login attempts"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid username or password.'
    default_code = 'login_failed'

    def __init__(self, detail=None, remaining_attempts=None):
        super().__init__(detail)
        self.remaining_attempts = remaining_attempts


class RegistrationError(AuthValidationError):
    """Exception for registration errors"""
    default_detail = 'Registration failed.'


class UserCreationError(APIException):
    """Exception for user creation errors"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to create user account.'
    default_code = 'user_creation_failed'


class EmailValidationError(AuthValidationError):
    """Exception for email validation errors"""
    default_detail = 'Invalid email data.'


class EmailSendError(APIException):
    """Exception for email sending errors"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to send email.'
    default_code = 'email_send_failed'


class AvatarUploadError(AuthValidationError):
    """Exception for avatar upload errors"""
    default_detail = 'Avatar upload failed.'


class ProfileUpdateError(AuthValidationError):
    """Exception for profile update errors"""
    default_detail = 'Profile update failed.'


class NoActiveSessionError(AuthValidationError):
    """Exception when no active session found"""
    default_detail = 'No active session found.'
