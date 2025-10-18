"""
Servicios core para SmartSales365
"""
import openai
import os
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone


class OpenAIService:
    """Servicio para integración con OpenAI"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def transcribe_audio(self, audio_file_path: str, language: str = 'es') -> Dict[str, Any]:
        """Transcribe audio a texto usando Whisper"""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'OpenAI API key no configurada'
                }
            
            with open(audio_file_path, 'rb') as audio_file:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            
            return {
                'success': True,
                'text': transcript.text,
                'language': language
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_voice_command(self, audio_file_path: str) -> Dict[str, Any]:
        """Procesa comando de voz y extrae intención"""
        try:
            # Transcribir audio
            transcription = self.transcribe_audio(audio_file_path)
            
            if not transcription['success']:
                return transcription
            
            text = transcription['text']
            
            # Procesar comando con GPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un asistente para SmartSales365. Analiza el siguiente comando de voz y extrae:
                        1. Tipo de acción (agregar_producto, buscar_producto, generar_reporte, etc.)
                        2. Parámetros específicos (nombre del producto, cantidad, etc.)
                        3. Confianza de la interpretación (0-1)
                        
                        Responde en formato JSON."""
                    },
                    {
                        "role": "user",
                        "content": f"Comando de voz: {text}"
                    }
                ],
                temperature=0.3
            )
            
            # Parsear respuesta
            import json
            try:
                intent_data = json.loads(response.choices[0].message.content)
            except:
                intent_data = {
                    'action': 'unknown',
                    'parameters': {},
                    'confidence': 0.0,
                    'original_text': text
                }
            
            return {
                'success': True,
                'transcription': text,
                'intent': intent_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def enhance_report_prompt(self, prompt: str) -> Dict[str, Any]:
        """Mejora un prompt de reporte usando GPT"""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'OpenAI API key no configurada'
                }
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un asistente para SmartSales365. Mejora el siguiente prompt de reporte:
                        1. Clarifica parámetros ambiguos
                        2. Sugiere filtros adicionales útiles
                        3. Optimiza la estructura del reporte
                        4. Mantén el formato original pero más claro
                        
                        Responde solo con el prompt mejorado."""
                    },
                    {
                        "role": "user",
                        "content": f"Prompt original: {prompt}"
                    }
                ],
                temperature=0.3
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'original_prompt': prompt,
                'enhanced_prompt': enhanced_prompt
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class VoiceCommandProcessor:
    """Procesador de comandos de voz para el carrito"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    def process_cart_command(self, audio_file_path: str) -> Dict[str, Any]:
        """Procesa comando de voz para el carrito"""
        try:
            # Procesar con OpenAI
            result = self.openai_service.process_voice_command(audio_file_path)
            
            if not result['success']:
                return result
            
            intent = result['intent']
            action = intent.get('action', 'unknown')
            parameters = intent.get('parameters', {})
            confidence = intent.get('confidence', 0.0)
            
            # Procesar según la acción
            if action == 'agregar_producto':
                return self._process_add_product(parameters, confidence)
            elif action == 'buscar_producto':
                return self._process_search_product(parameters, confidence)
            elif action == 'actualizar_cantidad':
                return self._process_update_quantity(parameters, confidence)
            elif action == 'remover_producto':
                return self._process_remove_product(parameters, confidence)
            else:
                return {
                    'success': False,
                    'error': 'Acción no reconocida',
                    'confidence': confidence
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_add_product(self, parameters: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Procesa agregar producto al carrito"""
        product_name = parameters.get('product_name', '')
        quantity = parameters.get('quantity', 1)
        
        if not product_name:
            return {
                'success': False,
                'error': 'Nombre del producto no especificado',
                'confidence': confidence
            }
        
        # Buscar producto por nombre
        from apps.products.models import Product
        try:
            product = Product.objects.filter(
                name__icontains=product_name,
                is_active=True
            ).first()
            
            if not product:
                return {
                    'success': False,
                    'error': f'Producto "{product_name}" no encontrado',
                    'confidence': confidence
                }
            
            return {
                'success': True,
                'action': 'add_product',
                'product_id': product.id,
                'product_name': product.name,
                'quantity': quantity,
                'confidence': confidence
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'confidence': confidence
            }
    
    def _process_search_product(self, parameters: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Procesa búsqueda de producto"""
        search_term = parameters.get('search_term', '')
        
        if not search_term:
            return {
                'success': False,
                'error': 'Término de búsqueda no especificado',
                'confidence': confidence
            }
        
        from apps.products.models import Product
        try:
            products = Product.objects.filter(
                name__icontains=search_term,
                is_active=True
            )[:10]  # Limitar a 10 resultados
            
            return {
                'success': True,
                'action': 'search_products',
                'products': [
                    {
                        'id': p.id,
                        'name': p.name,
                        'price': float(p.price),
                        'stock': p.stock
                    }
                    for p in products
                ],
                'confidence': confidence
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'confidence': confidence
            }
    
    def _process_update_quantity(self, parameters: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Procesa actualización de cantidad"""
        product_name = parameters.get('product_name', '')
        quantity = parameters.get('quantity', 1)
        
        if not product_name:
            return {
                'success': False,
                'error': 'Nombre del producto no especificado',
                'confidence': confidence
            }
        
        from apps.products.models import Product
        try:
            product = Product.objects.filter(
                name__icontains=product_name,
                is_active=True
            ).first()
            
            if not product:
                return {
                    'success': False,
                    'error': f'Producto "{product_name}" no encontrado',
                    'confidence': confidence
                }
            
            return {
                'success': True,
                'action': 'update_quantity',
                'product_id': product.id,
                'product_name': product.name,
                'quantity': quantity,
                'confidence': confidence
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'confidence': confidence
            }
    
    def _process_remove_product(self, parameters: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Procesa remover producto del carrito"""
        product_name = parameters.get('product_name', '')
        
        if not product_name:
            return {
                'success': False,
                'error': 'Nombre del producto no especificado',
                'confidence': confidence
            }
        
        from apps.products.models import Product
        try:
            product = Product.objects.filter(
                name__icontains=product_name,
                is_active=True
            ).first()
            
            if not product:
                return {
                    'success': False,
                    'error': f'Producto "{product_name}" no encontrado',
                    'confidence': confidence
                }
            
            return {
                'success': True,
                'action': 'remove_product',
                'product_id': product.id,
                'product_name': product.name,
                'confidence': confidence
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'confidence': confidence
            }


class NotificationService:
    """Servicio de notificaciones"""
    
    @staticmethod
    def send_low_stock_alert(product_id: str) -> bool:
        """Envía alerta de stock bajo"""
        try:
            from apps.products.models import Product
            from apps.notifications.models import Notification
            from django.contrib.auth.models import User
            
            product = Product.objects.get(id=product_id)
            
            if product.is_low_stock:
                # Crear notificación para administradores
                admins = User.objects.filter(is_staff=True)
                
                for admin in admins:
                    Notification.objects.create(
                        user=admin,
                        title=f"Stock Bajo: {product.name}",
                        message=f"El producto {product.name} tiene stock bajo ({product.stock} unidades). Stock mínimo: {product.min_stock}",
                        notification_type='warning'
                    )
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error enviando alerta de stock: {e}")
            return False
    
    @staticmethod
    def send_sale_notification(sale_id: str) -> bool:
        """Envía notificación de nueva venta"""
        try:
            from apps.sales.models import Sale
            from apps.notifications.models import Notification
            from django.contrib.auth.models import User
            
            sale = Sale.objects.get(id=sale_id)
            
            # Notificar a administradores
            admins = User.objects.filter(is_staff=True)
            
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title="Nueva Venta",
                    message=f"Se realizó una nueva venta por ${sale.total} al cliente {sale.client.name}",
                    notification_type='success'
                )
            
            return True
            
        except Exception as e:
            print(f"Error enviando notificación de venta: {e}")
            return False
