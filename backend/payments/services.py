import requests
from django.conf import settings
from typing import Dict, Optional, Tuple
import logging
import json
import os
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from pathlib import Path

logger = logging.getLogger(__name__)


class GMOClient:
    """Client for interacting with GMO Payment Gateway API"""
    
    def __init__(self):
        self.shop_id = settings.GMO_SHOP_ID
        self.shop_pass = settings.GMO_SHOP_PASS
        # Base URL: https://pt01.mul-pay.jp (test) or https://p01.mul-pay.jp (production)
        # API endpoints like EntryTranBrandtoken.idPass are appended
        self.api_endpoint = settings.GMO_API_ENDPOINT.rstrip('/')
        
    def _make_request(self, method: str, endpoint: str, data: Dict) -> Tuple[bool, Dict]:
        """
        Make HTTP request to GMO PG API with comprehensive error handling
        
        Args:
            method: HTTP method (typically POST)
            endpoint: API endpoint name (e.g., 'EntryTranBrandtoken.idPass')
            data: Request data dictionary
        
        Returns:
            Tuple of (success: bool, response_data: dict)
        
        Note:
            Shop ID and Shop Pass are required for API authentication.
            They are automatically added to the request data.
        """
        # GMO PG API format: base_url/endpoint.idPass
        # Example: https://pt01.mul-pay.jp/EntryTranBrandtoken.idPass
        url = f"{self.api_endpoint}/{endpoint}"
        
        # Validate credentials
        if not self.shop_id or not self.shop_pass:
            logger.error("GMO PG credentials not configured")
            return False, {'error': 'Payment gateway credentials not configured', 'error_code': 'CONFIG_ERROR'}
        
        # Add authentication
        data['ShopID'] = self.shop_id
        data['ShopPass'] = self.shop_pass
        
        try:
            response = requests.post(
                url,
                data=data,
                timeout=30,
                headers={'User-Agent': 'Django-ApplePay-POC/1.0'}
            )
            response.raise_for_status()
            
            # GMO PG returns form-encoded data (key=value format, one per line)
            result = {}
            if response.text:
                for line in response.text.strip().split('\n'):
                    line = line.strip()
                    if '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            result[key.strip()] = value.strip()
                        except ValueError:
                            logger.warning(f"Failed to parse line: {line}")
                            continue
            
            # Check for errors - GMO PG uses various error indicators
            error_code = result.get('ErrCode') or result.get('ErrorCode') or result.get('error_code')
            error_info = result.get('ErrInfo') or result.get('ErrorInfo') or result.get('error_info')
            
            if error_code or error_info or result.get('Status') == 'FAILURE':
                error_code = error_code or 'UNKNOWN_ERROR'
                error_info = error_info or result.get('ErrorMessage') or 'Unknown error from payment gateway'
                logger.error(f"GMO PG API Error: {error_code} - {error_info} | Full response: {result}")
                return False, {
                    'error_code': error_code,
                    'error_info': error_info,
                    'full_response': result
                }
            
            # Success indicators
            if 'AccessID' in result or 'CardID' in result or result.get('Status') in ['CAPTURE', 'AUTH', 'SUCCESS']:
                logger.info(f"GMO PG API Success: {endpoint}")
                return True, result
            
            # If no clear success/error indicators, assume success if no error codes
            if not error_code:
                logger.warning(f"GMO PG API ambiguous response: {result}")
                return True, result
            
            return False, {'error_code': error_code, 'error_info': error_info, 'full_response': result}
            
        except Timeout:
            logger.error(f"GMO PG API timeout: {url}")
            return False, {'error': 'Payment gateway request timeout', 'error_code': 'TIMEOUT'}
        except ConnectionError as e:
            logger.error(f"GMO PG API connection error: {str(e)}")
            return False, {'error': 'Payment gateway connection failed', 'error_code': 'CONNECTION_ERROR'}
        except HTTPError as e:
            logger.error(f"GMO PG API HTTP error: {e.response.status_code} - {str(e)}")
            return False, {
                'error': f'Payment gateway HTTP error: {e.response.status_code}',
                'error_code': f'HTTP_{e.response.status_code}'
            }
        except RequestException as e:
            logger.error(f"GMO PG API Request failed: {str(e)}")
            return False, {'error': f'Payment gateway request failed: {str(e)}', 'error_code': 'REQUEST_ERROR'}
        except Exception as e:
            logger.exception(f"Unexpected error in GMO PG API call: {str(e)}")
            return False, {'error': f'Unexpected error: {str(e)}', 'error_code': 'UNEXPECTED_ERROR'}
    
    def entry_tran_brandtoken(
        self,
        order_id: str,
        amount: int,
        currency: str = 'JPY'
    ) -> Tuple[bool, Dict]:
        """
        Initialize a transaction for Apple Pay (one-time payment)
        
        Args:
            order_id: Unique order identifier
            amount: Transaction amount (as integer, e.g., 1000 for 1000 JPY)
            currency: Currency code (default: JPY)
        
        Returns:
            Tuple of (success: bool, response_data with AccessID and AccessPass)
        """
        data = {
            'OrderID': order_id,
            'Amount': str(amount),
            'Currency': currency,
        }
        
        return self._make_request('POST', 'EntryTranBrandtoken.idPass', data)
    
    def exec_tran_brandtoken(
        self,
        access_id: str,
        access_pass: str,
        order_id: str,
        token: str
    ) -> Tuple[bool, Dict]:
        """
        Execute Apple Pay transaction using payment token
        
        Args:
            access_id: Access ID from EntryTranBrandtoken
            access_pass: Access Pass from EntryTranBrandtoken
            order_id: Order ID
            token: Apple Pay payment token (JSON string from frontend)
        
        Returns:
            Tuple of (success: bool, response_data with transaction status)
        """
        # Validate token format
        try:
            if isinstance(token, str):
                # Token should be JSON string, parse to validate
                token_data = json.loads(token)
                # GMO PG expects the token in specific format
                # Some implementations may need the token as-is or in specific format
                token_str = json.dumps(token_data)  # Re-serialize for consistency
            else:
                token_str = json.dumps(token)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Invalid token format: {str(e)}")
            return False, {
                'error': 'Invalid payment token format',
                'error_code': 'INVALID_TOKEN_FORMAT'
            }
        
        data = {
            'AccessID': access_id,
            'AccessPass': access_pass,
            'OrderID': order_id,
            'Token': token_str,
        }
        
        return self._make_request('POST', 'ExecTranBrandtoken.idPass', data)
    
    def save_member(
        self,
        member_id: str,
        member_name: str = ''
    ) -> Tuple[bool, Dict]:
        """
        Register a customer member for recurring payments
        
        Args:
            member_id: Unique member identifier
            member_name: Member name (optional)
        
        Returns:
            Tuple of (success: bool, response_data)
        """
        data = {
            'MemberID': member_id,
            'MemberName': member_name,
        }
        
        return self._make_request('POST', 'SaveMember.idPass', data)
    
    def save_card(
        self,
        member_id: str,
        token: str,
        seq_mode: str = '0'
    ) -> Tuple[bool, Dict]:
        """
        Save payment method for recurring billing using Apple Pay token
        
        Args:
            member_id: Member ID from SaveMember
            token: Apple Pay payment token
            seq_mode: Sequence mode (0: one-time, 1: recurring)
        
        Returns:
            Tuple of (success: bool, response_data with CardID)
        """
        data = {
            'MemberID': member_id,
            'Token': token,
            'SeqMode': seq_mode,
        }
        
        return self._make_request('POST', 'SaveCard.idPass', data)
    
    def exec_tran_recurring(
        self,
        order_id: str,
        member_id: str,
        card_id: str,
        amount: int,
        currency: str = 'JPY'
    ) -> Tuple[bool, Dict]:
        """
        Execute recurring payment using saved card information
        
        Args:
            order_id: Unique order identifier
            member_id: Member ID
            card_id: Card ID from SaveCard
            amount: Transaction amount (as integer)
            currency: Currency code (default: JPY)
        
        Returns:
            Tuple of (success: bool, response_data with transaction status)
        """
        data = {
            'OrderID': order_id,
            'MemberID': member_id,
            'CardID': card_id,
            'Amount': str(amount),
            'Currency': currency,
        }
        
        return self._make_request('POST', 'ExecTran.idPass', data)

    def alter_tran(
        self,
        access_id: str,
        access_pass: str,
        job_cd: str = 'VOID'
    ) -> Tuple[bool, Dict]:
        """
        Alter/cancel a transaction (for rollback when ExecTran fails)

        Args:
            access_id: Access ID from EntryTran
            access_pass: Access Pass from EntryTran
            job_cd: Job code - VOID (cancel), RETURN (refund), etc.

        Returns:
            Tuple of (success: bool, response_data)

        Note:
            VOID cancels a transaction before capture
            Use this for rollback when EntryTran succeeds but ExecTran fails
        """
        data = {
            'AccessID': access_id,
            'AccessPass': access_pass,
            'JobCd': job_cd,
        }

        return self._make_request('POST', 'AlterTran.idPass', data)


def validate_merchant_with_apple(validation_url: str) -> Tuple[bool, Dict]:
    """
    Validate merchant session with Apple's servers using Merchant Identity Certificate.
    
    This function sends the validation URL to Apple's validation servers and receives
    a properly signed merchant session that Apple Pay will accept.
    
    Args:
        validation_url: The validation URL provided by Apple Pay in the onvalidatemerchant event
        
    Returns:
        Tuple of (success: bool, merchant_session_dict or error_dict)
        
    Note:
        Requires APPLE_MERCHANT_IDENTITY_CERT_PATH and APPLE_MERCHANT_IDENTITY_KEY_PATH
        to be configured in settings with valid certificate files.
    """
    cert_path = getattr(settings, 'APPLE_MERCHANT_IDENTITY_CERT_PATH', None)
    key_path = getattr(settings, 'APPLE_MERCHANT_IDENTITY_KEY_PATH', None)
    
    if not cert_path or not key_path:
        logger.error("Merchant Identity Certificate paths not configured")
        return False, {
            'error': 'Merchant Identity Certificate not configured',
            'error_code': 'CERT_NOT_CONFIGURED'
        }
    
    # Check if certificate files exist
    cert_file = Path(cert_path)
    key_file = Path(key_path)
    
    if not cert_file.exists():
        logger.error(f"Merchant Identity Certificate not found: {cert_path}")
        return False, {
            'error': f'Merchant Identity Certificate file not found: {cert_path}',
            'error_code': 'CERT_FILE_NOT_FOUND'
        }
    
    if not key_file.exists():
        logger.error(f"Merchant Identity Key not found: {key_path}")
        return False, {
            'error': f'Merchant Identity Key file not found: {key_path}',
            'error_code': 'KEY_FILE_NOT_FOUND'
        }
    
    try:
        # Send validation request to Apple's servers with client certificate
        # Apple's validation endpoint requires:
        # 1. Merchant Identity Certificate for client certificate authentication
        # 2. POST body with merchantIdentifier (per Apple's 2025 documentation)
        merchant_id = getattr(settings, 'APPLE_MERCHANT_ID', None)
        
        if not merchant_id:
            logger.error("APPLE_MERCHANT_ID not configured")
            return False, {
                'error': 'Merchant ID not configured',
                'error_code': 'MERCHANT_ID_NOT_CONFIGURED'
            }
        
        logger.info(f"Validating merchant with Apple: {validation_url}")
        logger.info(f"Using Merchant ID: {merchant_id}")
        logger.info(f"Certificate: {cert_file}, Key: {key_file}")
        
        # Apple Pay merchant validation format (per Apple's official documentation 2023-2024):
        # POST to validation_url with:
        # 1. Client certificate authentication (Merchant Identity Certificate) - REQUIRED
        # 2. JSON body with required fields:
        #    - merchantIdentifier: Your merchant ID
        #    - displayName: Store name displayed to users
        #    - initiative: "web" for web-based transactions
        #    - initiativeContext: Fully qualified domain name
        
        # Extract domain from validation URL or use request domain
        import re
        from urllib.parse import urlparse, parse_qs
        
        # Try to extract domain from validation URL query parameters
        parsed_url = urlparse(validation_url)
        query_params = parse_qs(parsed_url.query)
        request_domain = None
        
        if 'initiativeContext' in query_params:
            request_domain = query_params['initiativeContext'][0]
        else:
            # Fallback: try regex extraction
            domain_match = re.search(r'initiativeContext=([^&]+)', validation_url)
            if domain_match:
                request_domain = domain_match.group(1)
        
        # If still no domain, use a default (for localhost testing)
        if not request_domain:
            request_domain = 'localhost'
            logger.warning("Domain not found in validation URL, using 'localhost' as fallback")
        
        # Per Apple's official documentation (2023-2024), the request body MUST include:
        request_body = {
            'merchantIdentifier': merchant_id,
            'displayName': 'Apple Pay POC',  # Store name displayed to users
            'initiative': 'web',  # Required: "web" for web-based transactions
            'initiativeContext': request_domain,  # Fully qualified domain name
        }
        
        logger.info(f"Request domain/initiativeContext: {request_domain}")
        logger.debug(f"Request body: {request_body}")
        
        # Attempt validation with SSL verification first
        # Per Apple's official documentation, the request MUST include the JSON body
        try:
            response = requests.post(
                validation_url,
                json=request_body,  # REQUIRED: JSON body with merchantIdentifier, displayName, initiative, initiativeContext
                cert=(str(cert_file), str(key_file)),  # REQUIRED: Client certificate authentication
                timeout=15,  # Increased timeout for Apple's servers
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Django-ApplePay-POC/1.0',
                    'Accept': 'application/json'
                },
                verify=True,  # Verify Apple's SSL certificate
            )
            response.raise_for_status()
        except requests.exceptions.SSLError as ssl_error:
            logger.error(f"SSL error during merchant validation: {str(ssl_error)}")
            # Try with verify=False for debugging (NOT recommended for production)
            logger.warning("Retrying with SSL verification disabled (for debugging only)")
            try:
                response = requests.post(
                    validation_url,
                    json=request_body,  # Include request body in retry
                    cert=(str(cert_file), str(key_file)),
                    timeout=15,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'Django-ApplePay-POC/1.0',
                        'Accept': 'application/json'
                    },
                    verify=False  # Only for debugging - remove in production
                )
                response.raise_for_status()
            except Exception as retry_error:
                logger.error(f"Retry also failed: {str(retry_error)}")
                raise
        except Exception as e:
            # Re-raise other exceptions to be handled by outer try-except
            raise
        
        # Apple returns the merchant session as JSON
        merchant_session = response.json()
        
        logger.info("Merchant validation successful with Apple")
        logger.debug(f"Merchant session received: {merchant_session}")
        return True, merchant_session
        
    except Timeout:
        logger.error(f"Apple merchant validation timeout: {validation_url}")
        return False, {
            'error': 'Apple validation request timeout',
            'error_code': 'VALIDATION_TIMEOUT'
        }
    except ConnectionError as e:
        logger.error(f"Apple merchant validation connection error: {str(e)}")
        return False, {
            'error': 'Failed to connect to Apple validation servers',
            'error_code': 'VALIDATION_CONNECTION_ERROR'
        }
    except HTTPError as e:
        logger.error(f"Apple merchant validation HTTP error: {e.response.status_code} - {e.response.text}")
        return False, {
            'error': f'Apple validation failed: HTTP {e.response.status_code}',
            'error_code': f'VALIDATION_HTTP_{e.response.status_code}',
            'response': e.response.text
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Apple merchant validation request error: {str(e)}")
        return False, {
            'error': f'Apple validation request failed: {str(e)}',
            'error_code': 'VALIDATION_REQUEST_ERROR'
        }
    except json.JSONDecodeError as e:
        logger.error(f"Apple merchant validation JSON decode error: {str(e)}")
        return False, {
            'error': 'Invalid response from Apple validation servers',
            'error_code': 'VALIDATION_JSON_ERROR'
        }
    except Exception as e:
        logger.exception(f"Unexpected error in Apple merchant validation: {str(e)}")
        return False, {
            'error': f'Unexpected validation error: {str(e)}',
            'error_code': 'VALIDATION_UNEXPECTED_ERROR'
        }

