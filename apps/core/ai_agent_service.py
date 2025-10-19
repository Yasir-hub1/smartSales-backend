"""
Servicio de Agente Inteligente para SmartSales365
Integra OpenAI para procesamiento de texto y voz
"""
import openai
import json
import os
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.utils import timezone
from apps.products.models import Product, Category
from apps.sales.models import Cart, CartItem
from apps.clients.models import Client


class AIAgentService:
    """Servicio principal del agente inteligente"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key
        else:
            raise ValueError("OPENAI_API_KEY no está configurada")
    
    def process_user_message(self, message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa mensaje del usuario y genera respuesta del agente
        """
        try:
            # Obtener contexto de productos y carrito
            products_context = self._get_products_context()
            cart_context = user_context.get('cart', {}) if user_context else {}
            
            # Crear prompt del sistema
            system_prompt = self._create_system_prompt(products_context, cart_context)
            
            # Procesar con GPT-4
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            agent_response = response.choices[0].message.content
            
            # Extraer acciones del agente
            actions = self._extract_actions(agent_response)
            
            # Limpiar la respuesta para el usuario
            clean_response = self._clean_response_for_user(agent_response)
            
            return {
                'success': True,
                'response': clean_response,
                'actions': actions,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': 'Lo siento, no pude procesar tu solicitud en este momento.'
            }
    
    def _clean_response_for_user(self, response: str) -> str:
        """Limpia la respuesta removiendo información técnica"""
        import re
        
        # Remover bloques de código JSON
        response = re.sub(r'```json\s*\{.*?\}\s*```', '', response, flags=re.DOTALL)
        
        # Remover líneas que contengan solo JSON
        lines = response.split('\n')
        clean_lines = []
        
        for line in lines:
            # Saltar líneas que parecen JSON puro
            if line.strip().startswith('{') and line.strip().endswith('}'):
                continue
            # Saltar líneas que contengan solo llaves o comas
            if line.strip() in ['{', '}', ',', ']', '[']:
                continue
            clean_lines.append(line)
        
        # Unir líneas y limpiar espacios extra
        clean_response = '\n'.join(clean_lines).strip()
        
        # Si la respuesta está vacía, usar un mensaje por defecto
        if not clean_response:
            return "¡Perfecto! He procesado tu solicitud. ¿Hay algo más en lo que pueda ayudarte? 😊"
        
        return clean_response
    
    def process_voice_command(self, audio_file_path: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa comando de voz y genera respuesta
        """
        try:
            # Transcribir audio con Whisper
            with open(audio_file_path, 'rb') as audio_file:
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"
                )
            
            transcribed_text = transcript.text
            
            # Procesar el texto transcrito
            return self.process_user_message(transcribed_text, user_context)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': 'No pude procesar tu comando de voz.'
            }
    
    def _get_products_context(self) -> str:
        """Obtiene contexto de productos disponibles"""
        try:
            products = Product.objects.filter(is_active=True)[:20]  # Limitar para el contexto
            categories = Category.objects.filter(is_active=True)
            
            products_info = []
            for product in products:
                products_info.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': float(product.price),
                    'stock': product.stock,
                    'category': product.category.name if product.category else 'Sin categoría'
                })
            
            categories_info = [{'id': cat.id, 'name': cat.name} for cat in categories]
            
            return json.dumps({
                'products': products_info,
                'categories': categories_info
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({'products': [], 'categories': []})
    
    def _create_system_prompt(self, products_context: str, cart_context: Dict[str, Any]) -> str:
        """Crea el prompt del sistema para el agente"""
        return f"""
Eres un asistente de ventas inteligente para SmartSales365. Tu objetivo es ayudar a los usuarios a:

1. **BUSCAR PRODUCTOS**: Encontrar productos por nombre, categoría o descripción
2. **AGREGAR AL CARRITO**: Añadir productos con cantidades específicas
3. **VER CARRITO**: Mostrar productos en el carrito con precios
4. **PROCESAR COMPRA**: Ayudar con el checkout y pago
5. **RECOMENDAR**: Sugerir productos basados en preferencias

**CONTEXTO DE PRODUCTOS DISPONIBLES:**
{products_context}

**CONTEXTO DEL CARRITO ACTUAL:**
{json.dumps(cart_context, ensure_ascii=False)}

**INSTRUCCIONES IMPORTANTES:**
- Responde de manera amigable y profesional
- NUNCA muestres código JSON o información técnica al usuario
- Usa emojis para hacer la conversación más amigable
- Mantén las respuestas concisas pero informativas
- EJECUTA las acciones directamente sin pedir confirmación
- Usa un tono conversacional y natural
- Sé directo y eficiente

**FORMATO DE RESPUESTA:**
- Responde al usuario de manera natural y amigable
- Al final de tu respuesta, incluye SOLO las acciones en formato JSON (sin mostrar al usuario):
```json
{{
    "actions": [
        {{
            "type": "search_products",
            "query": "término de búsqueda",
            "filters": {{"category": "id_categoria"}}
        }},
        {{
            "type": "add_to_cart",
            "product_id": 123,
            "quantity": 2
        }},
        {{
            "type": "show_cart"
        }},
        {{
            "type": "checkout"
        }}
    ]
}}
```

**EJEMPLOS DE RESPUESTAS CORRECTAS:**
- "¡Perfecto! He encontrado 3 laptops que podrían interesarte. Te muestro los detalles."
- "¡Listo! He agregado 2 unidades de iPhone 15 al carrito. Total: $2,000"
- "Tu carrito tiene 3 productos por un total de $1,500. Procediendo al pago..."
- "¡Compra realizada exitosamente! Tu pedido ha sido procesado por $1,500"

Responde al usuario de manera natural y útil, sin mostrar código técnico.
"""
    
    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """Extrae acciones del JSON en la respuesta del agente"""
        try:
            # Buscar JSON en la respuesta
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                actions_data = json.loads(json_match.group(1))
                return actions_data.get('actions', [])
            return []
        except Exception:
            return []
    
    def search_products(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Busca productos basado en query y filtros"""
        try:
            from django.db import models
            
            products = Product.objects.filter(is_active=True)
            
            if query:
                products = products.filter(
                    models.Q(name__icontains=query) |
                    models.Q(description__icontains=query)
                )
            
            if filters and filters.get('category'):
                products = products.filter(category_id=filters['category'])
            
            results = []
            for product in products[:10]:  # Limitar resultados
                results.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': float(product.price),
                    'stock': product.stock,
                    'category': product.category.name if product.category else 'Sin categoría',
                    'image': product.image.url if product.image else None
                })
            
            return results
            
        except Exception as e:
            return []
    
    def add_to_cart(self, product_id: int, quantity: int, cart_id: str = None) -> Dict[str, Any]:
        """Agrega producto al carrito"""
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            if product.stock < quantity:
                return {
                    'success': False,
                    'error': f'Stock insuficiente. Disponible: {product.stock}'
                }
            
            # Obtener o crear carrito
            if cart_id:
                try:
                    # Intentar buscar por ID primero, luego por session_key
                    try:
                        cart = Cart.objects.get(id=cart_id, is_active=True)
                    except Cart.DoesNotExist:
                        cart = Cart.objects.get(session_key=cart_id, is_active=True)
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(session_key=cart_id)
            else:
                cart = Cart.objects.create()
            
            # Agregar o actualizar item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity, 'price': product.price}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            # Los totales se calculan automáticamente por las propiedades
            
            total_price = float(cart_item.price * cart_item.quantity)
            
            return {
                'success': True,
                'message': f'¡Listo! He agregado {cart_item.quantity} unidades de {product.name} al carrito. Total: ${total_price:.2f}',
                'cart_item': {
                    'id': str(cart_item.id),
                    'product_name': product.name,
                    'quantity': cart_item.quantity,
                    'price': float(cart_item.price),
                    'total_price': total_price
                }
            }
            
        except Product.DoesNotExist:
            return {
                'success': False,
                'error': 'Producto no encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_cart_summary(self, cart_id: str) -> Dict[str, Any]:
        """Obtiene resumen del carrito"""
        try:
            # Intentar buscar por ID primero, luego por session_key
            try:
                cart = Cart.objects.get(id=cart_id, is_active=True)
            except Cart.DoesNotExist:
                cart = Cart.objects.get(session_key=cart_id, is_active=True)
            items = []
            
            for item in cart.items.all():
                items.append({
                    'id': item.id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'subtotal': float(item.price * item.quantity)
                })
            
            subtotal = float(cart.total_amount)
            final_total = subtotal
            
            return {
                'success': True,
                'cart': {
                    'id': str(cart.id),
                    'items': items,
                    'total_items': cart.total_items,
                    'subtotal': subtotal,
                    'final_total': final_total,
                    'summary': f"Tu carrito tiene {cart.total_items} productos. Subtotal: ${subtotal:.2f}, Total: ${final_total:.2f}"
                }
            }
            
        except Cart.DoesNotExist:
            return {
                'success': True,
                'cart': {
                    'items': [],
                    'total_items': 0,
                    'total_amount': 0,
                    'final_total': 0
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_checkout(self, cart_id: str, payment_method: str = 'cash') -> Dict[str, Any]:
        """Procesa el checkout del carrito"""
        try:
            # Intentar buscar por ID primero, luego por session_key
            try:
                cart = Cart.objects.get(id=cart_id, is_active=True)
            except Cart.DoesNotExist:
                cart = Cart.objects.get(session_key=cart_id, is_active=True)
            
            if not cart.items.exists():
                return {
                    'success': False,
                    'error': 'El carrito está vacío'
                }
            
            # Calcular totales
            subtotal = float(cart.total_amount)
            final_total = subtotal
            
            # Crear venta en el sistema
            from apps.sales.models import Sale, SaleItem
            from apps.clients.models import Client
            
            # Crear cliente anónimo si no existe
            try:
                client = Client.objects.filter(user=None).first()
                if not client:
                    client = Client.objects.create(
                        user=None,
                        name='Cliente Anónimo',
                        email='anonimo@tienda.com',
                        phone='000-000-0000'
                    )
            except Exception as e:
                # Si hay error, crear un cliente único
                client = Client.objects.create(
                    user=None,
                    name=f'Cliente Anónimo {cart_id[:8]}',
                    email=f'anonimo_{cart_id[:8]}@tienda.com',
                    phone='000-000-0000'
                )
            
            # Crear venta
            sale = Sale.objects.create(
                client=client,
                subtotal=subtotal,
                total=final_total,
                status='completed',
                payment_status='paid',
                notes=f'Compra realizada por agente inteligente - Carrito: {cart_id} - Método: {payment_method}'
            )
            
            # Crear items de venta
            for cart_item in cart.items.all():
                SaleItem.objects.create(
                    sale=sale,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.price
                )
            
            # Crear comprobante de venta
            from apps.sales.models import SaleReceipt
            receipt = SaleReceipt.objects.create(
                sale=sale,
                receipt_number=f"NV-{sale.id.hex[:8].upper()}"
            )
            
            # Generar PDF
            pdf_url = receipt.generate_pdf()
            
            # Desactivar carrito
            cart.is_active = False
            cart.save()
            
            return {
                'success': True,
                'message': f'¡Compra realizada exitosamente! Total pagado: ${final_total:.2f} (${payment_method})',
                'order': {
                    'sale_id': str(sale.id),
                    'cart_id': str(cart.id),
                    'subtotal': subtotal,
                    'total': final_total,
                    'payment_method': payment_method,
                    'items_count': cart.total_items,
                    'receipt_number': receipt.receipt_number,
                    'pdf_url': pdf_url
                }
            }
            
        except Cart.DoesNotExist:
            return {
                'success': False,
                'error': 'Carrito no encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
