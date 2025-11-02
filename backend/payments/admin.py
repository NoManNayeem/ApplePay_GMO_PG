from django.contrib import admin
from .models import Transaction, Subscription


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['transaction_id', 'gmo_order_id']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscription_id', 'amount', 'currency', 'billing_cycle', 'status', 'next_billing_date']
    list_filter = ['status', 'billing_cycle', 'created_at']
    search_fields = ['subscription_id', 'member_id', 'card_id']
    readonly_fields = ['subscription_id', 'created_at', 'updated_at']
