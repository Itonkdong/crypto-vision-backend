from rest_framework import status
from rest_framework.exceptions import APIException


class WatchlistException(APIException):
    """Base exception for watchlist operations"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Watchlist operation failed.'
    default_code = 'watchlist_error'


class WatchlistValidationError(APIException):
    """Exception for watchlist validation errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid watchlist data.'
    default_code = 'watchlist_validation_error'


class SymbolRequiredError(WatchlistValidationError):
    """Exception when symbol is missing or empty"""
    default_detail = 'Symbol is required and cannot be empty.'
    default_code = 'symbol_required'


class WatchlistOperationError(WatchlistException):
    """Exception for watchlist operation failures"""
    default_detail = 'Watchlist operation failed.'
    default_code = 'watchlist_operation_error'


class SubscriptionError(WatchlistOperationError):
    """Exception when subscription fails"""
    default_detail = 'Failed to subscribe to symbol.'
    default_code = 'subscription_error'


class UnsubscriptionError(WatchlistOperationError):
    """Exception when unsubscription fails"""
    default_detail = 'Failed to unsubscribe from symbol.'
    default_code = 'unsubscription_error'


class WatchlistNotFoundError(APIException):
    """Exception when watchlist data is not found"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Watchlist data not found.'
    default_code = 'watchlist_not_found'
