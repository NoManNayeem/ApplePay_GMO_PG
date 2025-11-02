"""
Custom exceptions for payment processing
"""
from rest_framework.exceptions import APIException
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class GMOAPIException(APIException):
    """Exception raised when GMO Payment Gateway API returns an error"""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'Payment gateway error occurred'
    default_code = 'payment_gateway_error'

    def __init__(self, error_code=None, error_info=None, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
            if error_info:
                detail = f"{self.default_detail}: {error_info}"
            if error_code:
                detail = f"{detail} (Error Code: {error_code})"
        
        super().__init__(detail, code)
        self.error_code = error_code
        self.error_info = error_info


class PaymentProcessingException(APIException):
    """Exception raised during payment processing"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Payment processing failed'
    default_code = 'payment_processing_failed'


class InvalidPaymentTokenException(APIException):
    """Exception raised when payment token is invalid"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid payment token'
    default_code = 'invalid_payment_token'


class MerchantValidationException(APIException):
    """Exception raised during merchant validation"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Merchant validation failed'
    default_code = 'merchant_validation_failed'


class SubscriptionException(APIException):
    """Exception raised for subscription-related errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Subscription operation failed'
    default_code = 'subscription_failed'


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF to provide consistent error responses
    """
    from rest_framework.views import exception_handler
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Add custom error structure
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
        }
        
        # Add error code if available
        if hasattr(exc, 'error_code'):
            custom_response_data['error_code'] = exc.error_code
        if hasattr(exc, 'error_info'):
            custom_response_data['error_info'] = exc.error_info
        
        # Add field-specific errors if validation error
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            custom_response_data['errors'] = exc.detail
        elif hasattr(exc, 'detail') and isinstance(exc.detail, list):
            custom_response_data['errors'] = exc.detail
        
        response.data = custom_response_data
        
        # Log the exception
        logger.error(
            f"API Exception: {exc.__class__.__name__} - {custom_response_data.get('message')}",
            extra={'context': context, 'status_code': response.status_code}
        )
    
    return response
