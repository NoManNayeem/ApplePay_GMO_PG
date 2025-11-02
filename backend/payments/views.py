import json
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Transaction, Subscription
from .serializers import (
    TransactionSerializer,
    SubscriptionSerializer,
    OneTimePaymentRequestSerializer,
    RecurringPaymentSetupSerializer,
    RecurringPaymentChargeSerializer,
)
from .services import GMOClient
from .config_validator import ConfigValidator


class ConfigStatusView(APIView):
    """
    Check configuration status of GMO PG and Apple Pay credentials
    Useful for debugging and setup verification
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get configuration validation status"""
        validation = ConfigValidator.validate_all()
        
        return Response({
            'all_valid': validation['all_valid'],
            'gmo_pg': {
                'valid': validation['gmo_pg']['valid'],
                'errors': validation['gmo_pg']['errors'],
                'warnings': validation['gmo_pg']['warnings'],
                'configured': {
                    'shop_id_set': validation['gmo_pg']['configured']['shop_id_set'],
                    'shop_pass_set': validation['gmo_pg']['configured']['shop_pass_set'],
                    'api_endpoint': validation['gmo_pg']['configured']['api_endpoint'],
                }
            },
            'apple_pay': {
                'valid': validation['apple_pay']['valid'],
                'errors': validation['apple_pay']['errors'],
                'warnings': validation['apple_pay']['warnings'],
                'configured': {
                    'merchant_id_set': validation['apple_pay']['configured']['merchant_id_set'],
                    # Don't expose full merchant ID in response
                }
            },
            'setup_guide': validation['setup_guide'],
        })


class MerchantSessionView(APIView):
    """
    Generate merchant session for Apple Pay validation
    This endpoint should return merchant session data for domain validation
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Validate configuration first
        apple_config = ConfigValidator.validate_apple_pay_config()
        
        if not apple_config['valid']:
            return Response(
                {
                    'error': 'Apple Pay not configured',
                    'errors': apple_config['errors'],
                    'setup_guide': 'See GMO_PG_APPLEPAY_SETUP.md for setup instructions',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # For POC, return basic merchant info
        # In production, this should generate proper merchant session using
        # Apple's Merchant Identity Certificate
        return Response({
            'merchant_id': settings.APPLE_MERCHANT_ID,
            'message': 'Merchant session endpoint - implement merchant session generation',
            'status': 'configured',
        })


class ValidateMerchantView(APIView):
    """
    Validate merchant session for Apple Pay
    This endpoint receives the validationURL from Apple Pay and should validate it
    with Apple's servers using the Merchant Identity Certificate.
    For POC/testing, we return a mock merchant session.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        validation_url = request.data.get('validation_url')
        
        if not validation_url:
            return Response(
                {'error': 'validation_url is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate configuration first
        apple_config = ConfigValidator.validate_apple_pay_config()
        
        if not apple_config['valid']:
            return Response(
                {
                    'error': 'Apple Pay not configured',
                    'errors': apple_config['errors'],
                    'setup_guide': 'See GMO_PG_APPLEPAY_SETUP.md for setup instructions',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        merchant_id = settings.APPLE_MERCHANT_ID
        
        # IMPORTANT: In production, you MUST:
        # 1. Send the validation_url to Apple's validation server
        # 2. Use your Merchant Identity Certificate to authenticate
        # 3. Receive and return the validated merchant session
        
        # For POC/testing, we create a mock merchant session
        # NOTE: This will work for testing, but may not work in all scenarios
        # Production requires proper validation with Apple's servers
        import time
        merchant_session = {
            'merchantSessionIdentifier': f'mock-session-{int(time.time())}',
            'displayName': 'Apple Pay POC',
            'domainName': 'localhost',
            'epochTimestamp': int(time.time() * 1000),
            'expiresAt': int((time.time() + 3600) * 1000),  # 1 hour
            'merchantIdentifier': merchant_id,
            'nonce': f'nonce-{int(time.time())}',
            'signature': f'signature-{int(time.time())}',  # Mock signature
        }
        
        return Response({
            'merchantSession': merchant_session,
            'merchant_id': merchant_id,
            'note': 'Using mock merchant session for POC. Production requires proper validation with Apple servers.',
        })


class OneTimePaymentSessionView(APIView):
    """
    Create payment session for one-time payment
    Validates merchant session for Apple Pay
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Validate configuration first
        apple_config = ConfigValidator.validate_apple_pay_config()
        gmo_config = ConfigValidator.validate_gmo_credentials()
        
        if not apple_config['valid']:
            return Response(
                {
                    'error': 'Apple Pay not configured',
                    'errors': apple_config['errors'],
                    'setup_guide': 'See GMO_PG_APPLEPAY_SETUP.md for setup instructions',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        if not gmo_config['valid']:
            return Response(
                {
                    'error': 'GMO Payment Gateway not configured',
                    'errors': gmo_config['errors'],
                    'setup_guide': 'See GMO_PG_APPLEPAY_SETUP.md for setup instructions',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # For POC, this validates that merchant is set up
        # In production, this would validate the merchant session properly
        merchant_id = settings.APPLE_MERCHANT_ID
        
        return Response({
            'merchant_id': merchant_id,
            'status': 'ready',
            'gmo_pg_configured': gmo_config['valid'],
            'warnings': apple_config['warnings'] + gmo_config['warnings'],
        })


class OneTimePaymentView(APIView):
    """
    Process one-time Apple Pay payment
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OneTimePaymentRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = serializer.validated_data['token']
        amount = serializer.validated_data['amount']
        currency = serializer.validated_data['currency']
        
        # Convert amount to integer (GMO PG expects integer, e.g., 1000 for 1000 JPY)
        amount_int = int(float(amount) * 100) if currency in ['USD', 'EUR'] else int(amount)
        
        # Create transaction record
        transaction = Transaction.objects.create(
            amount=amount,
            currency=currency,
            status='processing'
        )
        
        # Validate GMO credentials before processing
        gmo_config = ConfigValidator.validate_gmo_credentials()
        if not gmo_config['valid']:
            transaction.status = 'failed'
            transaction.error_code = 'CONFIG_ERROR'
            transaction.error_message = 'GMO Payment Gateway not configured: ' + ', '.join(gmo_config['errors'])
            transaction.save()
            
            return Response(
                {
                    'transaction_id': str(transaction.transaction_id),
                    'status': 'failed',
                    'error': 'Payment gateway not configured',
                    'errors': gmo_config['errors'],
                    'setup_guide': 'See GMO_PG_APPLEPAY_SETUP.md for setup instructions',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        gmo_client = GMOClient()
        order_id = f"ORDER_{transaction.transaction_id}"
        
        # Step 1: Entry transaction
        success, entry_response = gmo_client.entry_tran_brandtoken(
            order_id=order_id,
            amount=amount_int,
            currency=currency
        )
        
        if not success:
            transaction.status = 'failed'
            transaction.error_code = entry_response.get('error_code', 'ENTRY_ERROR')
            transaction.error_message = entry_response.get('error_info', 'Transaction entry failed')
            transaction.save()
            
            return Response({
                'transaction_id': str(transaction.transaction_id),
                'status': 'failed',
                'error': entry_response.get('error_info', 'Transaction entry failed'),
            }, status=status.HTTP_400_BAD_REQUEST)
        
        access_id = entry_response.get('AccessID')
        access_pass = entry_response.get('AccessPass')
        
        if not access_id or not access_pass:
            transaction.status = 'failed'
            transaction.error_message = 'Failed to get AccessID/AccessPass'
            transaction.save()
            
            return Response({
                'transaction_id': str(transaction.transaction_id),
                'status': 'failed',
                'error': 'Failed to initialize transaction',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Update transaction with GMO data
        transaction.gmo_access_id = access_id
        transaction.gmo_access_pass = access_pass
        transaction.gmo_order_id = order_id
        transaction.save()
        
        # Step 2: Execute transaction with Apple Pay token
        success, exec_response = gmo_client.exec_tran_brandtoken(
            access_id=access_id,
            access_pass=access_pass,
            order_id=order_id,
            token=token
        )
        
        if success and 'Status' in exec_response:
            transaction.status = 'completed'
            transaction.save()
            
            return Response({
                'transaction_id': str(transaction.transaction_id),
                'status': 'completed',
                'amount': str(amount),
                'currency': currency,
                'gmo_order_id': order_id,
            }, status=status.HTTP_200_OK)
        else:
            transaction.status = 'failed'
            transaction.error_code = exec_response.get('error_code', 'EXEC_ERROR')
            transaction.error_message = exec_response.get('error_info', 'Transaction execution failed')
            transaction.save()
            
            return Response({
                'transaction_id': str(transaction.transaction_id),
                'status': 'failed',
                'error': exec_response.get('error_info', 'Transaction execution failed'),
            }, status=status.HTTP_400_BAD_REQUEST)


class RecurringPaymentSetupView(APIView):
    """
    Setup recurring payment subscription using Apple Pay
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RecurringPaymentSetupSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = serializer.validated_data['token']
        amount = serializer.validated_data['amount']
        currency = serializer.validated_data['currency']
        billing_cycle = serializer.validated_data['billing_cycle']
        
        # Convert amount to integer
        amount_int = int(float(amount) * 100) if currency in ['USD', 'EUR'] else int(amount)
        
        # Create subscription record
        subscription = Subscription.objects.create(
            amount=amount,
            currency=currency,
            billing_cycle=billing_cycle,
            status='active'
        )
        
        # Calculate next billing date based on cycle
        next_billing = timezone.now()
        if billing_cycle.lower() == 'monthly':
            next_billing += timedelta(days=30)
        elif billing_cycle.lower() == 'yearly':
            next_billing += timedelta(days=365)
        
        subscription.next_billing_date = next_billing
        subscription.save()
        
        # Validate GMO credentials before processing
        gmo_config = ConfigValidator.validate_gmo_credentials()
        apple_config = ConfigValidator.validate_apple_pay_config()
        
        if not gmo_config['valid']:
            subscription.status = 'cancelled'
            subscription.save()
            
            return Response(
                {
                    'error': 'GMO Payment Gateway not configured',
                    'errors': gmo_config['errors'],
                    'setup_guide': 'See GMO_PG_APPLEPAY_SETUP.md for setup instructions',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        if not apple_config['valid']:
            subscription.status = 'cancelled'
            subscription.save()
            
            return Response(
                {
                    'error': 'Apple Pay not configured',
                    'errors': apple_config['errors'],
                    'setup_guide': 'See GMO_PG_APPLEPAY_SETUP.md for setup instructions',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        gmo_client = GMOClient()
        member_id = f"MEMBER_{subscription.subscription_id}"
        
        # Step 1: Save member
        success, member_response = gmo_client.save_member(
            member_id=member_id,
            member_name=f"Subscription {subscription.subscription_id}"
        )
        
        if not success:
            subscription.status = 'cancelled'
            subscription.save()
            
            return Response({
                'error': member_response.get('error_info', 'Failed to register member'),
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription.member_id = member_id
        subscription.save()
        
        # Step 2: Save card (payment method)
        success, card_response = gmo_client.save_card(
            member_id=member_id,
            token=token,
            seq_mode='1'  # 1 for recurring
        )
        
        if not success:
            subscription.status = 'cancelled'
            subscription.save()
            
            return Response({
                'error': card_response.get('error_info', 'Failed to save payment method'),
            }, status=status.HTTP_400_BAD_REQUEST)
        
        card_id = card_response.get('CardID')
        if not card_id:
            subscription.status = 'cancelled'
            subscription.save()
            
            return Response({
                'error': 'Failed to get Card ID',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        subscription.card_id = card_id
        subscription.save()
        
        # Step 3: Process initial charge
        order_id = f"ORDER_{subscription.subscription_id}_{int(timezone.now().timestamp())}"
        success, charge_response = gmo_client.exec_tran_recurring(
            order_id=order_id,
            member_id=member_id,
            card_id=card_id,
            amount=amount_int,
            currency=currency
        )
        
        if success and 'Status' in charge_response:
            subscription.last_billing_date = timezone.now()
            subscription.save()
            
            return Response({
                'subscription_id': str(subscription.subscription_id),
                'status': 'active',
                'member_id': member_id,
                'card_id': card_id,
                'amount': str(amount),
                'currency': currency,
                'billing_cycle': billing_cycle,
                'next_billing_date': subscription.next_billing_date.isoformat(),
            }, status=status.HTTP_200_OK)
        else:
            subscription.status = 'cancelled'
            subscription.save()
            
            return Response({
                'error': charge_response.get('error_info', 'Failed to process initial charge'),
            }, status=status.HTTP_400_BAD_REQUEST)


class RecurringPaymentChargeView(APIView):
    """
    Process recurring charge for existing subscription
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RecurringPaymentChargeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription_id = serializer.validated_data['subscription_id']
        amount = serializer.validated_data['amount']
        
        try:
            subscription = Subscription.objects.get(subscription_id=subscription_id)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if subscription.status != 'active':
            return Response(
                {'error': f'Subscription is {subscription.status}, cannot process charge'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        currency = subscription.currency
        amount_int = int(float(amount) * 100) if currency in ['USD', 'EUR'] else int(amount)
        
        gmo_client = GMOClient()
        order_id = f"ORDER_{subscription.subscription_id}_{int(timezone.now().timestamp())}"
        
        success, charge_response = gmo_client.exec_tran_recurring(
            order_id=order_id,
            member_id=subscription.member_id,
            card_id=subscription.card_id,
            amount=amount_int,
            currency=currency
        )
        
        if success and 'Status' in charge_response:
            subscription.last_billing_date = timezone.now()
            
            # Update next billing date
            if subscription.billing_cycle.lower() == 'monthly':
                subscription.next_billing_date = timezone.now() + timedelta(days=30)
            elif subscription.billing_cycle.lower() == 'yearly':
                subscription.next_billing_date = timezone.now() + timedelta(days=365)
            
            subscription.save()
            
            return Response({
                'subscription_id': str(subscription.subscription_id),
                'status': 'charged',
                'amount': str(amount),
                'currency': currency,
                'order_id': order_id,
                'next_billing_date': subscription.next_billing_date.isoformat(),
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': charge_response.get('error_info', 'Failed to process recurring charge'),
            }, status=status.HTTP_400_BAD_REQUEST)
