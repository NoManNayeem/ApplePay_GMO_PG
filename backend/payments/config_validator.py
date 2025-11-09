"""
Configuration validator for GMO PG and Apple Pay credentials
"""
from django.conf import settings
import logging
import os
from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.backends import default_backend

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
    def validate_certificate(cert_path: str, cert_name: str) -> dict:
        """
        Validate a certificate file exists, is readable, and check expiry

        Args:
            cert_path: Path to certificate file
            cert_name: Human-readable name for error messages

        Returns:
            dict with validation results
        """
        errors = []
        warnings = []
        info = {}

        if not cert_path:
            errors.append(f'{cert_name} path not configured')
            return {'valid': False, 'errors': errors, 'warnings': warnings, 'info': info}

        cert_file = Path(cert_path)

        # Check file exists
        if not cert_file.exists():
            errors.append(f'{cert_name} not found at {cert_path}')
            return {'valid': False, 'errors': errors, 'warnings': warnings, 'info': info}

        # Check file is readable
        if not os.access(cert_path, os.R_OK):
            errors.append(f'{cert_name} at {cert_path} is not readable')
            return {'valid': False, 'errors': errors, 'warnings': warnings, 'info': info}

        info['file_exists'] = True
        info['file_size'] = cert_file.stat().st_size

        # Try to read and parse certificate (only for .pem/.crt files)
        if cert_path.endswith(('.pem', '.crt', '.cer')):
            try:
                with open(cert_path, 'rb') as f:
                    cert_data = f.read()
                    cert = x509.load_pem_x509_certificate(cert_data, default_backend())

                    # Check expiry
                    from datetime import timezone
                    now = datetime.now(timezone.utc)

                    # Handle both offset-aware and offset-naive datetime objects
                    not_after = cert.not_valid_after_utc if hasattr(cert, 'not_valid_after_utc') else cert.not_valid_after
                    not_before = cert.not_valid_before_utc if hasattr(cert, 'not_valid_before_utc') else cert.not_valid_before

                    # Make offset-naive datetimes timezone-aware for comparison
                    if not_after.tzinfo is None:
                        not_after = not_after.replace(tzinfo=timezone.utc)
                    if not_before.tzinfo is None:
                        not_before = not_before.replace(tzinfo=timezone.utc)

                    info['not_before'] = not_before.isoformat()
                    info['not_after'] = not_after.isoformat()
                    info['subject'] = cert.subject.rfc4514_string()
                    info['issuer'] = cert.issuer.rfc4514_string()

                    if now < not_before:
                        errors.append(f'{cert_name} is not yet valid (valid from {not_before})')
                    elif now > not_after:
                        errors.append(f'{cert_name} has expired (expired on {not_after})')
                    elif now > not_after - timedelta(days=30):
                        warnings.append(f'{cert_name} expires soon (on {not_after})')

                    info['valid_certificate'] = True
            except Exception as e:
                warnings.append(f'Could not parse {cert_name}: {str(e)}')
                info['valid_certificate'] = False

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'info': info
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

        # Validate merchant identity certificates
        cert_path = getattr(settings, 'APPLE_MERCHANT_IDENTITY_CERT_PATH', '')
        key_path = getattr(settings, 'APPLE_MERCHANT_IDENTITY_KEY_PATH', '')

        cert_result = ConfigValidator.validate_certificate(cert_path, 'Merchant Identity Certificate')
        key_result = ConfigValidator.validate_certificate(key_path, 'Merchant Identity Private Key')

        errors.extend(cert_result['errors'])
        errors.extend(key_result['errors'])
        warnings.extend(cert_result['warnings'])
        warnings.extend(key_result['warnings'])

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'configured': {
                'merchant_id': merchant_id,
                'merchant_id_set': bool(merchant_id),
                'cert_file_exists': cert_result['info'].get('file_exists', False),
                'key_file_exists': key_result['info'].get('file_exists', False),
                'cert_info': cert_result['info'],
                'key_info': key_result['info'],
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

