import requests
from django.conf import settings
from typing import Dict, Optional, Tuple
import logging
import json
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError

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

