"""
Configuration validator for GMO PG and Apple Pay credentials
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates configuration for GMO PG and Apple Pay"""
    
    @staticmethod
    def validate_gmo_credentials() -> dict:
        """
        Validate GMO Payment Gateway credentials
        
        Returns:
            dict with 'valid' (bool) and 'errors' (list) keys
        """
        errors = []
        warnings = []
        
        shop_id = getattr(settings, 'GMO_SHOP_ID', '')
        shop_pass = getattr(settings, 'GMO_SHOP_PASS', '')
        api_endpoint = getattr(settings, 'GMO_API_ENDPOINT', '')
        
        if not shop_id:
            errors.append('GMO_SHOP_ID is not configured. Set it in .env file.')
        
        if not shop_pass:
            errors.append('GMO_SHOP_PASS is not configured. Set it in .env file.')
        
        if not api_endpoint:
            errors.append('GMO_API_ENDPOINT is not configured. Set it in .env file.')
        elif 'pt01.mul-pay.jp' in api_endpoint or 'pt01.mul-pay.com' in api_endpoint:
            warnings.append('Using test endpoint (pt01.mul-pay.jp). This is expected for development.')
        elif 'p01.mul-pay.jp' in api_endpoint or 'p01.mul-pay.com' in api_endpoint:
            warnings.append('Using production endpoint (p01.mul-pay.jp). Ensure all credentials are production-grade.')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'configured': {
                'shop_id_set': bool(shop_id),
                'shop_pass_set': bool(shop_pass),
                'api_endpoint': api_endpoint,
            }
        }
    
    @staticmethod
    def validate_apple_pay_config() -> dict:
        """
        Validate Apple Pay configuration
        
        Returns:
            dict with 'valid' (bool) and 'errors' (list) keys
        """
        errors = []
        warnings = []
        
        merchant_id = getattr(settings, 'APPLE_MERCHANT_ID', '')
        
        if not merchant_id:
            errors.append('APPLE_MERCHANT_ID is not configured. Set it in .env file.')
        elif not merchant_id.startswith('merchant.'):
            warnings.append(f'APPLE_MERCHANT_ID should start with "merchant." (current: {merchant_id})')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'configured': {
                'merchant_id': merchant_id,
                'merchant_id_set': bool(merchant_id),
            }
        }
    
    @staticmethod
    def validate_all() -> dict:
        """
        Validate all configuration
        
        Returns:
            dict with validation results for all components
        """
        gmo_result = ConfigValidator.validate_gmo_credentials()
        apple_result = ConfigValidator.validate_apple_pay_config()
        
        all_valid = gmo_result['valid'] and apple_result['valid']
        
        return {
            'all_valid': all_valid,
            'gmo_pg': gmo_result,
            'apple_pay': apple_result,
            'setup_guide': {
                'gmo_pg': 'See GMO_PG_APPLEPAY_SETUP.md for GMO PG setup instructions',
                'apple_pay': 'See GMO_PG_APPLEPAY_SETUP.md for Apple Pay setup instructions',
                'env_file': 'Copy env.txt to .env and configure your credentials',
            }
        }


# Validate on module import (warn only, don't fail)
validation_result = ConfigValidator.validate_all()
if not validation_result['all_valid']:
    logger.warning("⚠️  Configuration validation failed:")
    for error in validation_result['gmo_pg']['errors']:
        logger.warning(f"  GMO PG: {error}")
    for error in validation_result['apple_pay']['errors']:
        logger.warning(f"  Apple Pay: {error}")
    logger.warning("  See GMO_PG_APPLEPAY_SETUP.md for setup instructions")

