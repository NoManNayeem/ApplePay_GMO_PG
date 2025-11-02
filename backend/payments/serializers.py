from rest_framework import serializers
from .models import Transaction, Subscription


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'transaction_id', 'amount', 'currency', 'status',
            'gmo_order_id', 'error_code', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['transaction_id', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            'subscription_id', 'amount', 'currency', 'status',
            'billing_cycle', 'next_billing_date', 'last_billing_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['subscription_id', 'created_at', 'updated_at']


class OneTimePaymentRequestSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, help_text="Apple Pay payment token")
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=3, default='JPY')
    
    def validate_amount(self, value):
        """Validate that amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        if value > 99999999:
            raise serializers.ValidationError("Amount exceeds maximum limit.")
        return value
    
    def validate_currency(self, value):
        """Validate currency code"""
        supported_currencies = ['JPY', 'USD', 'EUR', 'GBP', 'AUD', 'CAD']
        if value.upper() not in supported_currencies:
            raise serializers.ValidationError(
                f"Currency must be one of: {', '.join(supported_currencies)}"
            )
        return value.upper()
    
    def validate_token(self, value):
        """Basic token validation"""
        if not value or len(value) < 10:
            raise serializers.ValidationError("Invalid payment token format.")
        try:
            import json
            json.loads(value)  # Validate JSON format
        except (json.JSONDecodeError, TypeError):
            raise serializers.ValidationError("Payment token must be valid JSON.")
        return value


class RecurringPaymentSetupSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, help_text="Apple Pay payment token")
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=3, default='JPY')
    billing_cycle = serializers.CharField(required=True, help_text="e.g., monthly, yearly")
    
    def validate_amount(self, value):
        """Validate that amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        if value > 99999999:
            raise serializers.ValidationError("Amount exceeds maximum limit.")
        return value
    
    def validate_currency(self, value):
        """Validate currency code"""
        supported_currencies = ['JPY', 'USD', 'EUR', 'GBP', 'AUD', 'CAD']
        if value.upper() not in supported_currencies:
            raise serializers.ValidationError(
                f"Currency must be one of: {', '.join(supported_currencies)}"
            )
        return value.upper()
    
    def validate_billing_cycle(self, value):
        """Validate billing cycle"""
        valid_cycles = ['monthly', 'yearly', 'weekly', 'daily']
        if value.lower() not in valid_cycles:
            raise serializers.ValidationError(
                f"Billing cycle must be one of: {', '.join(valid_cycles)}"
            )
        return value.lower()
    
    def validate_token(self, value):
        """Basic token validation"""
        if not value or len(value) < 10:
            raise serializers.ValidationError("Invalid payment token format.")
        try:
            import json
            json.loads(value)  # Validate JSON format
        except (json.JSONDecodeError, TypeError):
            raise serializers.ValidationError("Payment token must be valid JSON.")
        return value


class RecurringPaymentChargeSerializer(serializers.Serializer):
    subscription_id = serializers.UUIDField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

