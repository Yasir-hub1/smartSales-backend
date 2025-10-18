from rest_framework import serializers
from .models import PaymentMethod, Payment, PaymentRefund, StripeCustomer, PaymentWebhook


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer para métodos de pago"""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'code', 'is_active', 'is_online', 
            'icon', 'description', 'sort_order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagos"""
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    sale_id = serializers.CharField(source='sale.id', read_only=True)
    client_name = serializers.CharField(source='sale.client.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'sale', 'sale_id', 'payment_method', 'payment_method_name',
            'amount', 'currency', 'status', 'stripe_payment_intent_id',
            'stripe_charge_id', 'stripe_customer_id', 'metadata',
            'failure_reason', 'processed_at', 'failed_at', 'client_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_payment_intent_id', 'stripe_charge_id', 
            'stripe_customer_id', 'processed_at', 'failed_at', 
            'created_at', 'updated_at'
        ]


class CreatePaymentSerializer(serializers.ModelSerializer):
    """Serializer para crear pagos"""
    
    class Meta:
        model = Payment
        fields = [
            'sale', 'payment_method', 'amount', 'currency', 'metadata'
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value


class PaymentRefundSerializer(serializers.ModelSerializer):
    """Serializer para reembolsos"""
    payment_id = serializers.CharField(source='payment.id', read_only=True)
    
    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'payment', 'payment_id', 'amount', 'reason', 
            'status', 'stripe_refund_id', 'created_at'
        ]
        read_only_fields = ['id', 'stripe_refund_id', 'created_at']


class CreateRefundSerializer(serializers.ModelSerializer):
    """Serializer para crear reembolsos"""
    
    class Meta:
        model = PaymentRefund
        fields = ['payment', 'amount', 'reason']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value


class StripeCustomerSerializer(serializers.ModelSerializer):
    """Serializer para clientes de Stripe"""
    
    class Meta:
        model = StripeCustomer
        fields = [
            'id', 'user', 'client', 'stripe_customer_id', 
            'email', 'name', 'created_at'
        ]
        read_only_fields = ['id', 'stripe_customer_id', 'created_at']


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """Serializer para webhooks"""
    
    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'stripe_event_id', 'event_type', 'processed', 
            'data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentIntentSerializer(serializers.Serializer):
    """Serializer para crear Payment Intent"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='MXN')
    customer_email = serializers.EmailField(required=False)
    customer_name = serializers.CharField(max_length=200, required=False)
    metadata = serializers.JSONField(default=dict, required=False)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value


class ConfirmPaymentSerializer(serializers.Serializer):
    """Serializer para confirmar pagos"""
    payment_intent_id = serializers.CharField(max_length=100)
    payment_method_id = serializers.CharField(max_length=100, required=False)