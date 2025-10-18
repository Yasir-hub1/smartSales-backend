from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.sales.models import Sale
import uuid


class PaymentMethod(BaseModel):
    """Métodos de pago disponibles"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    code = models.CharField(max_length=50, unique=True, verbose_name='Código')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_online = models.BooleanField(default=False, verbose_name='Pago Online')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Icono')
    description = models.TextField(blank=True, verbose_name='Descripción')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    
    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class Payment(BaseModel):
    """Pagos del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments', verbose_name='Venta')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name='Método de Pago')
    
    # Información del pago
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    currency = models.CharField(max_length=3, default='MXN', verbose_name='Moneda')
    
    # Estado del pago
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado')
    ], default='pending', verbose_name='Estado')
    
    # Información de Stripe
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, verbose_name='ID Payment Intent')
    stripe_charge_id = models.CharField(max_length=100, blank=True, verbose_name='ID Charge')
    stripe_customer_id = models.CharField(max_length=100, blank=True, verbose_name='ID Customer')
    
    # Metadatos
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Metadatos')
    failure_reason = models.TextField(blank=True, verbose_name='Razón del Fallo')
    
    # Timestamps
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Procesado en')
    failed_at = models.DateTimeField(null=True, blank=True, verbose_name='Falló en')
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pago {self.id} - {self.amount} {self.currency}"
    
    @property
    def is_successful(self):
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        return self.status in ['failed', 'cancelled']
    
    @property
    def is_pending(self):
        return self.status in ['pending', 'processing']


class PaymentRefund(BaseModel):
    """Reembolsos de pagos"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds', verbose_name='Pago')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    reason = models.CharField(max_length=100, blank=True, verbose_name='Razón')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendiente'),
        ('succeeded', 'Exitoso'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado')
    ], default='pending', verbose_name='Estado')
    
    # Información de Stripe
    stripe_refund_id = models.CharField(max_length=100, blank=True, verbose_name='ID Refund')
    
    class Meta:
        verbose_name = 'Reembolso'
        verbose_name_plural = 'Reembolsos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reembolso {self.id} - {self.amount}"


class StripeCustomer(BaseModel):
    """Clientes de Stripe"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Cliente')
    stripe_customer_id = models.CharField(max_length=100, unique=True, verbose_name='ID Customer')
    email = models.EmailField(verbose_name='Email')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    
    class Meta:
        verbose_name = 'Cliente Stripe'
        verbose_name_plural = 'Clientes Stripe'
    
    def __str__(self):
        return f"{self.name} ({self.email})"


class PaymentWebhook(BaseModel):
    """Webhooks de Stripe"""
    stripe_event_id = models.CharField(max_length=100, unique=True, verbose_name='ID Event', default='')
    event_type = models.CharField(max_length=100, verbose_name='Tipo de Evento', default='')
    processed = models.BooleanField(default=False, verbose_name='Procesado')
    data = models.JSONField(default=dict, verbose_name='Datos')
    
    class Meta:
        verbose_name = 'Webhook Stripe'
        verbose_name_plural = 'Webhooks Stripe'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Webhook {self.stripe_event_id} - {self.event_type}"