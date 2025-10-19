"""
API Views para el Agente Inteligente
"""
import json
import os
import tempfile
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .ai_agent_service import AIAgentService
from apps.sales.models import Cart
from apps.products.models import Product


@api_view(['POST'])
@permission_classes([AllowAny])
def chat_with_agent(request):
    """
    Endpoint para chat con el agente inteligente
    """
    try:
        message = request.data.get('message', '')
        cart_id = request.data.get('cart_id', '')
        
        if not message:
            return Response({
                'error': 'Mensaje requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener contexto del carrito
        cart_context = {}
        if cart_id:
            try:
                # Intentar buscar por ID primero, luego por session_key
                try:
                    cart = Cart.objects.get(id=cart_id, is_active=True)
                except Cart.DoesNotExist:
                    cart = Cart.objects.get(session_key=cart_id, is_active=True)
                
                cart_context = {
                    'cart': {
                        'id': str(cart.id),
                        'total_items': cart.total_items,
                        'total_amount': float(cart.total_amount),
                        'items': [
                            {
                                'product_name': item.product.name,
                                'quantity': item.quantity,
                                'price': float(item.price)
                            }
                            for item in cart.items.all()
                        ]
                    }
                }
            except Cart.DoesNotExist:
                cart_context = {'cart': {}}
        
        # Procesar con el agente
        agent_service = AIAgentService()
        result = agent_service.process_user_message(message, cart_context)
        
        return Response(result)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def process_voice_command(request):
    """
    Endpoint para procesar comandos de voz
    """
    try:
        if 'audio' not in request.FILES:
            return Response({
                'error': 'Archivo de audio requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        audio_file = request.FILES['audio']
        cart_id = request.data.get('cart_id', '')
        
        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Obtener contexto del carrito
            cart_context = {}
            if cart_id:
                try:
                    # Intentar buscar por ID primero, luego por session_key
                    try:
                        cart = Cart.objects.get(id=cart_id, is_active=True)
                    except Cart.DoesNotExist:
                        cart = Cart.objects.get(session_key=cart_id, is_active=True)
                    
                    cart_context = {
                        'cart': {
                            'id': str(cart.id),
                            'total_items': cart.total_items,
                            'total_amount': float(cart.total_amount),
                            'items': [
                                {
                                    'product_name': item.product.name,
                                    'quantity': item.quantity,
                                    'price': float(item.price)
                                }
                                for item in cart.items.all()
                            ]
                        }
                    }
                except Cart.DoesNotExist:
                    cart_context = {'cart': {}}
            
            # Procesar con el agente
            agent_service = AIAgentService()
            result = agent_service.process_voice_command(temp_file_path, cart_context)
            
            return Response(result)
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def execute_agent_action(request):
    """
    Endpoint para ejecutar acciones del agente
    """
    try:
        action = request.data.get('action', {})
        cart_id = request.data.get('cart_id', '')
        
        if not action:
            return Response({
                'error': 'Acción requerida'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        agent_service = AIAgentService()
        action_type = action.get('type')
        
        if action_type == 'search_products':
            query = action.get('query', '')
            filters = action.get('filters', {})
            results = agent_service.search_products(query, filters)
            return Response({
                'success': True,
                'results': results
            })
        
        elif action_type == 'add_to_cart':
            product_id = action.get('product_id')
            quantity = action.get('quantity', 1)
            result = agent_service.add_to_cart(product_id, quantity, cart_id)
            return Response(result)
        
        elif action_type == 'show_cart':
            result = agent_service.get_cart_summary(cart_id)
            return Response(result)
        
        elif action_type == 'checkout':
            # Detectar tipo de pago
            payment_method = action.get('payment_method', 'cash')
            
            # Solo abrir modal para tarjetas
            if payment_method in ['credit_card', 'debit_card', 'card']:
                return Response({
                    'success': True,
                    'redirect': True,
                    'message': 'Redirigiendo al proceso de pago...',
                    'action': 'open_checkout_modal'
                })
            else:
                # Procesar automáticamente efectivo y transferencia
                result = agent_service.process_checkout(cart_id, payment_method)
                return Response(result)
        
        else:
            return Response({
                'error': 'Tipo de acción no soportado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_agent_suggestions(request):
    """
    Endpoint para obtener sugerencias del agente
    """
    try:
        cart_id = request.GET.get('cart_id', '')
        
        # Obtener contexto del carrito
        cart_context = {}
        if cart_id:
            try:
                # Intentar buscar por ID primero, luego por session_key
                try:
                    cart = Cart.objects.get(id=cart_id, is_active=True)
                except Cart.DoesNotExist:
                    cart = Cart.objects.get(session_key=cart_id, is_active=True)
                
                cart_context = {
                    'cart': {
                        'id': str(cart.id),
                        'total_items': cart.total_items,
                        'total_amount': float(cart.total_amount)
                    }
                }
            except Cart.DoesNotExist:
                cart_context = {'cart': {}}
        
        # Generar sugerencias basadas en el contexto
        suggestions = []
        
        if cart_context.get('cart', {}).get('total_items', 0) == 0:
            suggestions = [
                "¿Qué productos te interesan?",
                "Puedo ayudarte a buscar productos específicos",
                "¿Te gustaría ver nuestras categorías?"
            ]
        else:
            suggestions = [
                "¿Quieres agregar más productos?",
                "¿Te gustaría proceder al pago?",
                "¿Necesitas ver el resumen de tu carrito?"
            ]
        
        return Response({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
