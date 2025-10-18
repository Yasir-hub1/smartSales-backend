import stripe
import logging
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from .models import Payment, PaymentMethod, StripeCustomer, PaymentRefund, PaymentWebhook

logger = logging.getLogger(__name__)

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Servicio para manejar operaciones con Stripe"""
    
    @staticmethod
    def create_payment_intent(amount, currency='MXN', customer_email=None, customer_name=None, metadata=None):
        """Crear Payment Intent en Stripe"""
        try:
            # Convertir a centavos para Stripe
            amount_cents = int(amount * 100)
            
            intent_data = {
                'amount': amount_cents,
                'currency': currency.lower(),
                'automatic_payment_methods': {
                    'enabled': True,
                },
                'metadata': metadata or {}
            }
            
            # Agregar información del cliente si está disponible
            if customer_email:
                intent_data['receipt_email'] = customer_email
                intent_data['metadata']['customer_email'] = customer_email
            
            if customer_name:
                intent_data['metadata']['customer_name'] = customer_name
            
            payment_intent = stripe.PaymentIntent.create(**intent_data)
            
            logger.info(f"Payment Intent creado: {payment_intent.id}")
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creando Payment Intent: {str(e)}")
            raise Exception(f"Error procesando pago: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado creando Payment Intent: {str(e)}")
            raise Exception(f"Error inesperado: {str(e)}")
    
    @staticmethod
    def confirm_payment_intent(payment_intent_id):
        """Confirmar Payment Intent"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status == 'requires_confirmation':
                payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            logger.info(f"Payment Intent confirmado: {payment_intent_id}")
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Error confirmando Payment Intent: {str(e)}")
            raise Exception(f"Error confirmando pago: {str(e)}")
    
    @staticmethod
    def get_payment_intent(payment_intent_id):
        """Obtener Payment Intent"""
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            logger.error(f"Error obteniendo Payment Intent: {str(e)}")
            raise Exception(f"Error obteniendo pago: {str(e)}")
    
    @staticmethod
    def create_customer(email, name=None, metadata=None):
        """Crear cliente en Stripe"""
        try:
            customer_data = {
                'email': email,
                'metadata': metadata or {}
            }
            
            if name:
                customer_data['name'] = name
            
            customer = stripe.Customer.create(**customer_data)
            logger.info(f"Cliente creado en Stripe: {customer.id}")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creando cliente: {str(e)}")
            raise Exception(f"Error creando cliente: {str(e)}")
    
    @staticmethod
    def get_or_create_customer(email, name=None, user=None, client=None):
        """Obtener o crear cliente en Stripe"""
        try:
            # Buscar cliente existente en nuestra base de datos
            stripe_customer = StripeCustomer.objects.filter(email=email).first()
            
            if stripe_customer:
                return stripe_customer
            
            # Crear nuevo cliente en Stripe
            customer = StripeService.create_customer(email, name)
            
            # Guardar en nuestra base de datos
            stripe_customer = StripeCustomer.objects.create(
                user=user,
                client=client,
                stripe_customer_id=customer.id,
                email=email,
                name=name or email
            )
            
            return stripe_customer
            
        except Exception as e:
            logger.error(f"Error obteniendo/creando cliente: {str(e)}")
            raise Exception(f"Error con cliente: {str(e)}")
    
    @staticmethod
    def create_refund(payment_intent_id, amount=None, reason=None):
        """Crear reembolso en Stripe"""
        try:
            refund_data = {
                'payment_intent': payment_intent_id
            }
            
            if amount:
                # Convertir a centavos
                refund_data['amount'] = int(amount * 100)
            
            if reason:
                refund_data['reason'] = reason
            
            refund = stripe.Refund.create(**refund_data)
            logger.info(f"Reembolso creado: {refund.id}")
            return refund
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creando reembolso: {str(e)}")
            raise Exception(f"Error procesando reembolso: {str(e)}")
    
    @staticmethod
    def handle_webhook(event_data):
        """Manejar webhook de Stripe"""
        try:
            event_type = event_data.get('type')
            event_id = event_data.get('id')
            
            # Verificar si ya procesamos este evento
            if PaymentWebhook.objects.filter(stripe_event_id=event_id).exists():
                logger.warning(f"Webhook ya procesado: {event_id}")
                return
            
            # Guardar webhook
            webhook = PaymentWebhook.objects.create(
                stripe_event_id=event_id,
                event_type=event_type,
                data=event_data
            )
            
            # Procesar según el tipo de evento
            if event_type == 'payment_intent.succeeded':
                StripeService._handle_payment_succeeded(event_data)
            elif event_type == 'payment_intent.payment_failed':
                StripeService._handle_payment_failed(event_data)
            elif event_type == 'payment_intent.canceled':
                StripeService._handle_payment_canceled(event_data)
            
            webhook.processed = True
            webhook.save()
            
            logger.info(f"Webhook procesado: {event_id} - {event_type}")
            
        except Exception as e:
            logger.error(f"Error procesando webhook: {str(e)}")
            raise Exception(f"Error procesando webhook: {str(e)}")
    
    @staticmethod
    def _handle_payment_succeeded(event_data):
        """Manejar pago exitoso"""
        try:
            payment_intent = event_data['data']['object']
            payment_intent_id = payment_intent['id']
            
            # Buscar pago en nuestra base de datos
            payment = Payment.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if payment:
                payment.status = 'completed'
                payment.processed_at = timezone.now()
                payment.save()
                
                # Actualizar estado de la venta
                if payment.sale:
                    payment.sale.payment_status = 'paid'
                    payment.sale.save()
                
                logger.info(f"Pago marcado como completado: {payment.id}")
            
        except Exception as e:
            logger.error(f"Error manejando pago exitoso: {str(e)}")
    
    @staticmethod
    def _handle_payment_failed(event_data):
        """Manejar pago fallido"""
        try:
            payment_intent = event_data['data']['object']
            payment_intent_id = payment_intent['id']
            failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Pago fallido')
            
            # Buscar pago en nuestra base de datos
            payment = Payment.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if payment:
                payment.status = 'failed'
                payment.failure_reason = failure_reason
                payment.failed_at = timezone.now()
                payment.save()
                
                logger.info(f"Pago marcado como fallido: {payment.id}")
            
        except Exception as e:
            logger.error(f"Error manejando pago fallido: {str(e)}")
    
    @staticmethod
    def _handle_payment_canceled(event_data):
        """Manejar pago cancelado"""
        try:
            payment_intent = event_data['data']['object']
            payment_intent_id = payment_intent['id']
            
            # Buscar pago en nuestra base de datos
            payment = Payment.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if payment:
                payment.status = 'cancelled'
                payment.failed_at = timezone.now()
                payment.save()
                
                logger.info(f"Pago marcado como cancelado: {payment.id}")
            
        except Exception as e:
            logger.error(f"Error manejando pago cancelado: {str(e)}")


class PaymentService:
    """Servicio para manejar pagos en el sistema"""
    
    @staticmethod
    def create_payment(sale, payment_method, amount, currency='MXN', metadata=None):
        """Crear pago en el sistema"""
        try:
            # Obtener método de pago
            method = PaymentMethod.objects.get(code=payment_method)
            
            # Crear pago
            payment = Payment.objects.create(
                sale=sale,
                payment_method=method,
                amount=amount,
                currency=currency,
                metadata=metadata or {}
            )
            
            logger.info(f"Pago creado: {payment.id}")
            return payment
            
        except PaymentMethod.DoesNotExist:
            raise Exception("Método de pago no válido")
        except Exception as e:
            logger.error(f"Error creando pago: {str(e)}")
            raise Exception(f"Error creando pago: {str(e)}")
    
    @staticmethod
    def process_stripe_payment(payment, customer_email=None, customer_name=None):
        """Procesar pago con Stripe"""
        try:
            # Crear Payment Intent
            payment_intent = StripeService.create_payment_intent(
                amount=float(payment.amount),
                currency=payment.currency,
                customer_email=customer_email,
                customer_name=customer_name,
                metadata={
                    'payment_id': str(payment.id),
                    'sale_id': str(payment.sale.id)
                }
            )
            
            # Actualizar pago con información de Stripe
            payment.stripe_payment_intent_id = payment_intent.id
            payment.status = 'processing'
            payment.save()
            
            logger.info(f"Pago procesado con Stripe: {payment.id}")
            return payment_intent
            
        except Exception as e:
            logger.error(f"Error procesando pago con Stripe: {str(e)}")
            payment.status = 'failed'
            payment.failure_reason = str(e)
            payment.failed_at = timezone.now()
            payment.save()
            raise Exception(f"Error procesando pago: {str(e)}")
    
    @staticmethod
    def confirm_payment(payment_intent_id):
        """Confirmar pago"""
        try:
            # Confirmar en Stripe
            payment_intent = StripeService.confirm_payment_intent(payment_intent_id)
            
            # Buscar pago en nuestra base de datos
            payment = Payment.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if payment:
                if payment_intent.status == 'succeeded':
                    payment.status = 'completed'
                    payment.processed_at = timezone.now()
                    payment.save()
                    
                    # Actualizar estado de la venta
                    payment.sale.payment_status = 'paid'
                    payment.sale.save()
                    
                    logger.info(f"Pago confirmado: {payment.id}")
                    return payment
                else:
                    payment.status = 'failed'
                    payment.failure_reason = f"Estado inesperado: {payment_intent.status}"
                    payment.failed_at = timezone.now()
                    payment.save()
                    
                    raise Exception(f"Pago no exitoso: {payment_intent.status}")
            
            raise Exception("Pago no encontrado")
            
        except Exception as e:
            logger.error(f"Error confirmando pago: {str(e)}")
            raise Exception(f"Error confirmando pago: {str(e)}")
    
    @staticmethod
    def create_refund(payment, amount=None, reason=None):
        """Crear reembolso"""
        try:
            if not payment.stripe_payment_intent_id:
                raise Exception("Pago no tiene Payment Intent de Stripe")
            
            # Crear reembolso en Stripe
            refund = StripeService.create_refund(
                payment_intent_id=payment.stripe_payment_intent_id,
                amount=amount or payment.amount,
                reason=reason
            )
            
            # Crear reembolso en nuestra base de datos
            payment_refund = PaymentRefund.objects.create(
                payment=payment,
                amount=amount or payment.amount,
                reason=reason or '',
                status='succeeded',
                stripe_refund_id=refund.id
            )
            
            # Actualizar estado del pago
            payment.status = 'refunded'
            payment.save()
            
            logger.info(f"Reembolso creado: {payment_refund.id}")
            return payment_refund
            
        except Exception as e:
            logger.error(f"Error creando reembolso: {str(e)}")
            raise Exception(f"Error creando reembolso: {str(e)}")
