from django.db import models
from django.utils import timezone
import uuid


class Transaction(models.Model):
    """Model to store one-time payment transactions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='JPY')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    gmo_access_id = models.CharField(max_length=50, blank=True, null=True)
    gmo_access_pass = models.CharField(max_length=50, blank=True, null=True)
    gmo_order_id = models.CharField(max_length=50, blank=True, null=True)
    error_code = models.CharField(max_length=20, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency} - {self.status}"


class Subscription(models.Model):
    """Model to store recurring payment subscriptions"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    subscription_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member_id = models.CharField(max_length=50, help_text="GMO PG Member ID")
    card_id = models.CharField(max_length=50, help_text="GMO PG Card ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='JPY')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    billing_cycle = models.CharField(max_length=20, help_text="e.g., monthly, yearly")
    next_billing_date = models.DateTimeField(blank=True, null=True)
    last_billing_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Subscription {self.subscription_id} - {self.amount} {self.currency}/{self.billing_cycle} - {self.status}"
