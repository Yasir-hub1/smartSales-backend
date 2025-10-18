from django.contrib import admin
from .models import PaymentMethod, Payment, PaymentRefund, StripeCustomer, PaymentWebhook


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'is_online', 'sort_order']
    list_filter = ['is_active', 'is_online']
    search_fields = ['name', 'code']
    ordering = ['sort_order', 'name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'sale', 'payment_method', 'amount', 'currency', 
        'status', 'created_at', 'processed_at'
    ]
    list_filter = ['status', 'currency', 'payment_method', 'created_at']
    search_fields = ['id', 'sale__id', 'stripe_payment_intent_id']
    readonly_fields = [
        'id', 'stripe_payment_intent_id', 'stripe_charge_id', 
        'stripe_customer_id', 'processed_at', 'failed_at', 
        'created_at', 'updated_at'
    ]
    ordering = ['-created_at']


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'payment__id', 'stripe_refund_id']
    readonly_fields = ['id', 'stripe_refund_id', 'created_at']
    ordering = ['-created_at']


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'stripe_customer_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'stripe_customer_id']
    readonly_fields = ['stripe_customer_id', 'created_at']
    ordering = ['-created_at']


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = ['stripe_event_id', 'event_type', 'processed', 'created_at']
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['stripe_event_id', 'event_type']
    readonly_fields = ['stripe_event_id', 'created_at']
    ordering = ['-created_at']