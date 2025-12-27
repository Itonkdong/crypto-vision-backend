from rest_framework import status
from rest_framework.exceptions import APIException


class MarketDataException(APIException):
    """Base exception for market data operations"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Market data operation failed.'
    default_code = 'market_data_error'


class SymbolNotFoundError(APIException):
    """Exception when requested symbol is not found"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Symbol not found.'
    default_code = 'symbol_not_found'


class PriceDataNotFoundError(APIException):
    """Exception when no price data is available"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'No price data available for this symbol.'
    default_code = 'price_data_not_found'


class AlertNotFoundError(APIException):
    """Exception when price alert is not found"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Alert not found.'
    default_code = 'alert_not_found'


class AlertValidationError(APIException):
    """Exception for price alert validation errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid alert data.'
    default_code = 'alert_validation_error'


class MarketDataProcessingError(MarketDataException):
    """Exception for data processing errors"""
    default_detail = 'Error processing market data.'
    default_code = 'data_processing_error'


class InvalidParameterError(APIException):
    """Exception for invalid query parameters"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid parameter provided.'
    default_code = 'invalid_parameter'
