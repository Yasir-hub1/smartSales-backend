from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
import json
from django.conf import settings

from .models import PaymentMethod, Payment, PaymentRefund, StripeCustomer
from .serializers import (
    PaymentMethodSerializer, PaymentSerializer, CreatePaymentSerializer,
    PaymentRefundSerializer, CreateRefundSerializer, StripeCustomerSerializer,
    PaymentIntentSerializer, ConfirmPaymentSerializer
)
from .services import StripeService, PaymentService


class PaymentMethodListView(generics.ListAPIView):
    """Listar métodos de pago disponibles"""
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]


class PaymentListCreateView(generics.ListCreateAPIView):
    """Listar y crear pagos"""
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreatePaymentSerializer
        return PaymentSerializer
    
    def perform_create(self, serializer):
        serializer.save()


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualizar y eliminar pago"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([AllowAny])
def create_payment_intent(request):
    """Crear Payment Intent para Stripe"""
    try:
        serializer = PaymentIntentSerializer(data=request.data)
        if serializer.is_valid():
            payment_intent = StripeService.create_payment_intent(
                amount=serializer.validated_data['amount'],
                currency=serializer.validated_data['currency'],
                customer_email=serializer.validated_data.get('customer_email'),
                customer_name=serializer.validated_data.get('customer_name'),
                metadata=serializer.validated_data.get('metadata', {})
            )
            
            return Response({
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'status': payment_intent.status
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_payment(request):
    """Confirmar pago con Stripe"""
    try:
        serializer = ConfirmPaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = PaymentService.confirm_payment(
                serializer.validated_data['payment_intent_id']
            )
            
            return Response({
                'success': True,
                'payment_id': str(payment.id),
                'status': payment.status,
                'amount': float(payment.amount)
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_sale_payment(request, sale_id):
    """Procesar pago de una venta"""
    try:
        from apps.sales.models import Sale
        
        # Obtener venta
        try:
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            return Response({'error': 'Venta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener datos del pago
        payment_method = request.data.get('payment_method', 'stripe')
        customer_email = request.data.get('customer_email')
        customer_name = request.data.get('customer_name')
        
        # Crear pago
        payment = PaymentService.create_payment(
            sale=sale,
            payment_method=payment_method,
            amount=sale.total,
            currency='MXN',
            metadata={
                'sale_id': str(sale.id),
                'customer_email': customer_email or '',
                'customer_name': customer_name or ''
            }
        )
        
        # Procesar según método de pago
        if payment_method == 'stripe':
            payment_intent = PaymentService.process_stripe_payment(
                payment=payment,
                customer_email=customer_email,
                customer_name=customer_name
            )
            
            return Response({
                'payment_id': str(payment.id),
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'status': payment.status
            }, status=status.HTTP_201_CREATED)
        else:
            # Para métodos de pago offline (efectivo, transferencia)
            payment.status = 'completed'
            payment.processed_at = timezone.now()
            payment.save()
            
            sale.payment_status = 'paid'
            sale.save()
            
            return Response({
                'payment_id': str(payment.id),
                'status': payment.status,
                'message': 'Pago procesado exitosamente'
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_refund(request, payment_id):
    """Crear reembolso"""
    try:
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Pago no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateRefundSerializer(data=request.data)
        if serializer.is_valid():
            refund = PaymentService.create_refund(
                payment=payment,
                amount=serializer.validated_data.get('amount'),
                reason=serializer.validated_data.get('reason', '')
            )
            
            return Response({
                'refund_id': str(refund.id),
                'amount': float(refund.amount),
                'status': refund.status
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_status(request, payment_id):
    """Obtener estado de un pago"""
    try:
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Pago no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Si es un pago de Stripe, obtener estado actualizado
        if payment.stripe_payment_intent_id:
            try:
                payment_intent = StripeService.get_payment_intent(payment.stripe_payment_intent_id)
                
                # Actualizar estado si es necesario
                if payment_intent.status == 'succeeded' and payment.status != 'completed':
                    payment.status = 'completed'
                    payment.processed_at = timezone.now()
                    payment.save()
                    
                    payment.sale.payment_status = 'paid'
                    payment.sale.save()
                elif payment_intent.status == 'requires_payment_method' and payment.status != 'failed':
                    payment.status = 'failed'
                    payment.failed_at = timezone.now()
                    payment.save()
                    
            except Exception as e:
                # Si hay error obteniendo el estado de Stripe, usar el estado local
                pass
        
        return Response({
            'payment_id': str(payment.id),
            'status': payment.status,
            'amount': float(payment.amount),
            'currency': payment.currency,
            'processed_at': payment.processed_at,
            'failed_at': payment.failed_at
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_payment_methods(request):
    """Obtener métodos de pago disponibles"""
    try:
        methods = PaymentMethod.objects.filter(is_active=True).order_by('sort_order')
        serializer = PaymentMethodSerializer(methods, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Webhook de Stripe
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """Manejar webhooks de Stripe"""
    
    def post(self, request):
        import stripe
        
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            # Payload inválido
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            # Firma inválida
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        
        # Procesar webhook
        try:
            StripeService.handle_webhook(event)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# Vista para webhook (compatible con función)
@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Webhook de Stripe (versión función)"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    try:
        StripeService.handle_webhook(event)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)