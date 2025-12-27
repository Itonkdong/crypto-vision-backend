from typing import Dict, Any, Optional, Union
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpRequest

from helpers.abstract import AbstractService
from helpers.constants import MAX_LOGIN_ATTEMPTS, LOCKOUT_DURATION_SECONDS, LOCKOUT_DURATION_MINUTES
from .email_service import send_alert_email
from ..exceptions.auth_exceptions import (
    LoginValidationError, AccountLockedException, LoginFailedException,
    RegistrationError, UserCreationError, EmailValidationError, EmailSendError,
    AvatarUploadError, ProfileUpdateError, NoActiveSessionError
)
from auth.models import UserProfile

import logging
logger = logging.getLogger(__name__)


class AuthService(AbstractService):
    
    
    def get_client_ip(self,request: HttpRequest) -> str:
        """Get the client IP address from the request."""
        x_forwarded_for: Optional[str] = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip: str = x_forwarded_for.split(',')[0]
        else:
            ip: str = request.META.get('REMOTE_ADDR', '')
        return ip

    def get_failed_attempts_key(self,username: str, ip_address: str) -> str:
        """Generate cache key for failed login attempts."""
        return f'failed_login_attempts_{username}_{ip_address}'

    def get_lockout_key(self,username: str, ip_address: str) -> str:
        """Generate cache key for account lockout."""
        return f'account_locked_{username}_{ip_address}'

    def is_account_locked(self,username: str, ip_address: str) -> bool:
        """Check if account is locked due to too many failed attempts."""
        lockout_key: str = self.get_lockout_key(username, ip_address)
        return cache.get(lockout_key) is not None

    def get_remaining_lockout_time(self,username: str, ip_address: str) -> int:
        """Get remaining lockout time in seconds."""
        lockout_key: str = self.get_lockout_key(username, ip_address)
        ttl: Optional[int] = cache.ttl(lockout_key)
        return max(0, ttl) if ttl else 0

    def increment_failed_attempts(self,username: str, ip_address: str) -> bool:
        """Increment failed login attempts and lock account if threshold reached."""
        attempts_key: str = self.get_failed_attempts_key(username, ip_address)
        lockout_key: str = self.get_lockout_key(username, ip_address)

        # Get current attempts count
        attempts: int = cache.get(attempts_key, 0)
        attempts += 1

        # Store attempts count with expiration
        cache.set(attempts_key, attempts, timeout=LOCKOUT_DURATION_SECONDS)

        # If threshold reached, lock the account
        if attempts >= MAX_LOGIN_ATTEMPTS:
            cache.set(lockout_key, True, timeout=LOCKOUT_DURATION_SECONDS)
            return True  # Account is now locked

        return False  # Account not locked yet

    def reset_failed_attempts(self,username: str, ip_address: str) -> None:
        """Reset failed login attempts on successful login."""
        attempts_key: str = self.get_failed_attempts_key(username, ip_address)
        lockout_key: str = self.get_lockout_key(username, ip_address)
        cache.delete(attempts_key)
        cache.delete(lockout_key)

    def get_failed_attempts_count(self,username: str, ip_address: str) -> int:
        """Get current failed login attempts count."""
        attempts_key: str = self.get_failed_attempts_key(username, ip_address)
        return cache.get(attempts_key, 0)

    def validate_login_data(self,username: Optional[str], password: Optional[str]) -> None:
        """Validate login credentials - raises exception if invalid."""
        if not username or not password:
            raise LoginValidationError('Username and password are required.')

    def check_account_lockout(self,username: str, ip_address: str) -> None:
        """Check if account is locked - raises exception if locked."""
        if self.is_account_locked(username, ip_address):
            remaining_time: int = self.get_remaining_lockout_time(username, ip_address)
            remaining_minutes: int = (remaining_time + 59) // 60  # Round up to nearest minute

            raise AccountLockedException(
                f'Сметката е блокирана поради {MAX_LOGIN_ATTEMPTS} неуспешни обиди за најава. Обидете се повторно за {remaining_minutes} минути.',
                remaining_time=remaining_time
            )

    def perform_login(self,request: HttpRequest, username: str, password: str) -> Dict[str, Any]:
        """Perform authentication and login."""
        user: Optional[User] = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session.set_expiry(1800)
            return {
                'success': True,
                'user': user,
                'message': 'Login successful.'
            }
        return {
            'success': False,
            'user': None
        }

    def handle_failed_login(self,username: str, ip_address: str) -> None:
        """Handle failed login attempt - raises appropriate exception."""
        is_locked: bool = self.increment_failed_attempts(username, ip_address)
        attempts_count: int = self.get_failed_attempts_count(username, ip_address)
        remaining_attempts: int = MAX_LOGIN_ATTEMPTS - attempts_count

        if is_locked:
            raise AccountLockedException(
                f'Сметката е блокирана поради {MAX_LOGIN_ATTEMPTS} неуспешни обиди за најава. Обидете се повторно за {LOCKOUT_DURATION_MINUTES} минути.',
                remaining_time=LOCKOUT_DURATION_SECONDS
            )
        else:
            error_message: str = 'Невалидно корисничко име или лозинка.'
            if remaining_attempts > 0:
                error_message += f' Остануваат {remaining_attempts} обиди пред блокирање.'

            raise LoginFailedException(error_message, remaining_attempts=remaining_attempts)

    def perform_logout(self,request: HttpRequest) -> Dict[str, str]:
        """Perform user logout - raises exception if no active session."""
        if not request.user.is_authenticated:
            raise NoActiveSessionError('No active session found.')

        logout(request)
        return {'message': 'Logout successful.'}

    def validate_registration_data(self,username: Optional[str], password: Optional[str], email: Optional[str] = None) -> None:
        """Validate registration data - raises exception if invalid."""
        if not username or not password:
            raise RegistrationError('Username and password are required.')

        if len(password) < 8:
            raise RegistrationError('Password must be at least 8 characters long.')

        if User.objects.filter(username=username).exists():
            raise RegistrationError('Username already exists.')

        if email and User.objects.filter(email=email).exists():
            raise RegistrationError('Email already registered.')

    def create_user(self,username: str, password: str, email: str = '', first_name: str = '', last_name: str = '') -> User:
        """Create a new user - raises exception if creation fails."""
        try:
            user: User = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            return user
        except Exception as e:
            raise UserCreationError(f'Registration failed: {str(e)}')

    def perform_registration_login(self,request: HttpRequest, user: User) -> None:
        """Log in user after successful registration."""
        login(request, user)
        request.session.set_expiry(1800)

    def validate_alert_email_data(self,data: Dict[str, Any]) -> Dict[str, Union[str, float]]:
        """Validate alert email data - raises exception if invalid."""
        user_email: Optional[str] = data.get('email')
        crypto: Optional[str] = data.get('crypto')
        symbol: Optional[str] = data.get('symbol')
        condition: Optional[str] = data.get('condition')

        if not all([user_email, crypto, symbol, condition]):
            raise EmailValidationError('Missing required fields')

        try:
            target_price: float = float(data.get('target_price', 0))
            current_price: float = float(data.get('current_price', 0))
            return {
                'user_email': user_email,
                'crypto': crypto,
                'symbol': symbol,
                'condition': condition,
                'target_price': target_price,
                'current_price': current_price
            }
        except (ValueError, TypeError):
            raise EmailValidationError('Invalid price values')

    def send_alert_email_notification(self,user_email: str, crypto: str, symbol: str, condition: str, target_price: float, current_price: float) -> None:
        """Send alert email notification - raises exception if sending fails."""
        try:
            success: bool = send_alert_email(
                user_email,
                crypto,
                symbol,
                condition,
                target_price,
                current_price
            )

            if not success:
                logger.error(f'Failed to send email to {user_email} for {crypto} ({symbol})')
                raise EmailSendError('Failed to send email. Check server logs for details.')

        except Exception as e:
            logger.error(f'Exception sending alert email: {str(e)}', exc_info=True)
            raise EmailSendError(f'Error sending email: {str(e)}')

    def validate_avatar_upload(self,request: HttpRequest) -> Any:
        """Validate avatar upload request - raises exception if invalid."""
        avatar_file = request.FILES.get("avatar")
        if not avatar_file:
            raise AvatarUploadError('No file uploaded')
        return avatar_file

    def upload_user_avatar(self,user: User, avatar_file: Any) -> UserProfile:
        """Upload user avatar."""
        profile: UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.avatar = avatar_file
        profile.save()
        return profile

    def validate_user_update_data(self,user: User, data: Dict[str, Any]) -> None:
        """Validate user update data - raises exception if invalid."""
        email: str = data.get('email', '')

        if email:
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                raise ProfileUpdateError('This email is already registered to another user.')

    def update_user_profile(self,user: User, data: Dict[str, Any]) -> User:
        """Update user profile."""
        email: str = data.get('email', '')
        first_name: str = data.get('first_name', '')
        last_name: str = data.get('last_name', '')

        if email:
            user.email = email
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name

        user.save()
        return user


service = AuthService()


def get_auth_service() -> AuthService:
    """
    Factory and Singleton method to get the AuthService instance.

    This method implements both Factory and Singleton design patterns:
    - Factory Pattern: Creates and returns service instances based on type
    - Singleton Pattern: Ensures only one instance exists throughout the application lifecycle

    Returns:
        AuthService: The singleton instance of AuthService

    Note:
        Thread-safe singleton implementation ensures concurrent access safety.
    """
    return service