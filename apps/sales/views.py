from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Cart, CartItem, Sale, SaleItem, SaleReceipt
from apps.clients.models import Client
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer,
    SaleSerializer, CreateSaleSerializer, SaleReceiptSerializer, SaleStatsSerializer
)

def get_or_create_cart(request):
    """Helper para obtener o crear carrito"""
    if request.user.is_authenticated:
        # Para usuarios autenticados, buscar carrito activo del usuario
        try:
            cart = Cart.objects.filter(
                user=request.user, 
                is_active=True
            ).order_by('-created_at').first()
            
            if cart:
                return cart
            
            # Si no existe, crear uno nuevo
            cart = Cart.objects.create(
                user=request.user,
                is_active=True,
                session_key=request.session.session_key or 'anonymous'
            )
            return cart
        except Cart.MultipleObjectsReturned:
            # Si hay múltiples, tomar el más reciente y desactivar los demás
            carts = Cart.objects.filter(
                user=request.user,
                is_active=True
            ).order_by('-created_at')
            
            cart = carts.first()
            # Desactivar los demás carritos
            carts.exclude(id=cart.id).update(is_active=False)
            return cart
    else:
        # Para usuarios anónimos, usar session_key
        session_key = request.session.session_key or 'anonymous'
        
        try:
            # Intentar obtener el carrito más reciente
            cart = Cart.objects.filter(
                session_key=session_key,
                is_active=True,
                user__isnull=True
            ).order_by('-created_at').first()
            
            if cart:
                return cart
            
            # Si no existe, crear uno nuevo
            cart = Cart.objects.create(
                session_key=session_key,
                is_active=True,
                user=None
            )
            return cart
        except Cart.MultipleObjectsReturned:
            # Si hay múltiples, tomar el más reciente y desactivar los demás
            carts = Cart.objects.filter(
                session_key=session_key,
                is_active=True,
                user__isnull=True
            ).order_by('-created_at')
            
            cart = carts.first()
            # Desactivar los demás carritos
            carts.exclude(id=cart.id).update(is_active=False)
            return cart


class CartListCreateView(generics.ListCreateAPIView):
    """Listar y crear carritos"""
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active', 'client']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualizar y eliminar carrito"""
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, cart_id):
    """Agregar producto al carrito"""
    try:
        cart = Cart.objects.get(id=cart_id, is_active=True)
    except Cart.DoesNotExist:
        return Response({'error': 'Carrito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            from apps.products.models import Product
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar stock disponible
        if product.stock < quantity:
            return Response(
                {'error': 'Stock insuficiente'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Agregar al carrito
        cart_item = cart.add_product(product, quantity)
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, cart_id, item_id):
    """Actualizar cantidad de item en el carrito"""
    try:
        cart = Cart.objects.get(id=cart_id, is_active=True)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({'error': 'Item no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UpdateCartItemSerializer(data=request.data)
    if serializer.is_valid():
        quantity = serializer.validated_data['quantity']
        
        # Verificar stock disponible
        if cart_item.product.stock < quantity:
            return Response(
                {'error': 'Stock insuficiente'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, cart_id, item_id):
    """Remover item del carrito"""
    try:
        cart = Cart.objects.get(id=cart_id, is_active=True)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({'error': 'Item no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    cart_item.delete()
    return Response({'message': 'Item removido del carrito'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart(request, cart_id):
    """Limpiar carrito"""
    try:
        cart = Cart.objects.get(id=cart_id, is_active=True)
    except Cart.DoesNotExist:
        return Response({'error': 'Carrito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    cart.clear()
    return Response({'message': 'Carrito limpiado'})


class SaleListCreateView(generics.ListCreateAPIView):
    """Listar y crear ventas"""
    queryset = Sale.objects.select_related('client', 'user').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'client', 'user']
    search_fields = ['id', 'client__name', 'notes', 'transaction_id']
    ordering_fields = ['created_at', 'total', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateSaleSerializer
        return SaleSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Crear venta con manejo de cliente"""
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Obtener datos del request
            data = request.data.copy()
            client_data = data.get('client', {})
            
            logger.info(f"📝 Creando venta - Datos recibidos:")
            logger.info(f"   client_data: {client_data}")
            logger.info(f"   Tipo de client_data: {type(client_data)}")
            
            # Si se proporciona información del cliente, crear o obtener cliente
            if isinstance(client_data, dict) and client_data.get('name'):
                logger.info(f"   ✅ Cliente detectado como diccionario con nombre: {client_data.get('name')}")
                client = self._get_or_create_client(client_data)
                logger.info(f"   ✅ Cliente obtenido/creado: ID={client.id}, Nombre={client.name}, Email={client.email}")
                data['client'] = client.id
            elif isinstance(client_data, (int, str)):
                # Si es un ID, verificar que existe
                logger.info(f"   Cliente detectado como ID: {client_data}")
                try:
                    client = Client.objects.get(id=client_data)
                    logger.info(f"   ✅ Cliente encontrado: ID={client.id}, Nombre={client.name}")
                except Client.DoesNotExist:
                    logger.error(f"   ❌ Cliente no encontrado con ID: {client_data}")
                    return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.warning(f"   ⚠️ Cliente no válido o vacío. client_data: {client_data}")
                # Si no hay cliente, crear uno anónimo
                client = Client.objects.create(
                    name='Cliente Anónimo',
                    email='',
                    phone='',
                    address='',
                    city='',
                    country='México',
                    user=None
                )
                logger.info(f"   ✅ Cliente anónimo creado: ID={client.id}")
                data['client'] = client.id
            
            # Calcular totales si no se proporcionan
            if 'items' in data and not data.get('total'):
                total = sum(item.get('price', 0) * item.get('quantity', 0) for item in data['items'])
                data['subtotal'] = total
                data['total'] = total
            
            # Establecer valores por defecto
            data.setdefault('status', 'completed')
            data.setdefault('payment_status', 'paid')
            data.setdefault('discount', 0)
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            sale = serializer.save(user=request.user)
            
            # Verificar que el cliente se asoció correctamente
            logger.info(f"✅ Venta creada: ID={sale.id}")
            logger.info(f"   Cliente asociado: ID={sale.client.id if sale.client else 'None'}, Nombre={sale.client.name if sale.client else 'None'}")
            logger.info(f"   Total: {sale.total}, Items: {sale.items.count()}")
            
            # Refrescar la venta desde la BD para asegurar que tenemos los datos actualizados
            sale.refresh_from_db()
            logger.info(f"   Después de refresh - Cliente: ID={sale.client.id if sale.client else 'None'}, Nombre={sale.client.name if sale.client else 'None'}")
            
            # Crear comprobante
            SaleReceipt.objects.create(
                sale=sale,
                receipt_number=f"NV-{sale.id}",
                qr_code=f"https://smartsales365.com/receipt/{sale.id}"
            )
            
            # Enviar notificación push cuando la venta está completada
            if sale.status == 'completed':
                try:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Venta {sale.id} completada. Enviando notificaciones...")
                    from apps.core.services import NotificationService
                    result = NotificationService.send_sale_notification(str(sale.id))
                    if result:
                        logger.info(f"Notificaciones enviadas exitosamente para venta {sale.id}")
                    else:
                        logger.warning(f"Notificaciones retornaron False para venta {sale.id}")
                except Exception as notif_error:
                    # No fallar la creación de la venta si hay error en notificaciones
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error enviando notificación de venta {sale.id}: {notif_error}", exc_info=True)
            
            # Serializar la venta con el cliente incluido
            sale_serializer = SaleSerializer(sale)
            sale_data = sale_serializer.data
            
            logger.info(f"📤 Datos de la venta a retornar:")
            logger.info(f"   ID: {sale_data.get('id')}")
            logger.info(f"   Cliente ID: {sale_data.get('client')}")
            logger.info(f"   Cliente Nombre: {sale_data.get('client_name')}")
            logger.info(f"   Total: {sale_data.get('total')}")
            
            return Response(sale_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Error creando venta: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_or_create_client(self, client_data):
        """Obtener o crear cliente"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔍 _get_or_create_client - Datos recibidos: {client_data}")
        
        # Validar que tenemos al menos el nombre
        if not client_data.get('name'):
            logger.error(f"❌ No se proporcionó nombre del cliente")
            raise ValueError('El nombre del cliente es requerido')
        
        try:
            # Buscar por email primero si se proporciona
            if client_data.get('email'):
                logger.info(f"   Buscando cliente por email: {client_data['email']}")
                try:
                    client = Client.objects.get(email=client_data['email'])
                    logger.info(f"   ✅ Cliente encontrado por email: ID={client.id}, Nombre={client.name}")
                    
                    # Actualizar datos si es necesario
                    updated = False
                    if client_data.get('name') and client.name != client_data['name']:
                        logger.info(f"   Actualizando nombre: '{client.name}' -> '{client_data['name']}'")
                        client.name = client_data['name']
                        updated = True
                    if client_data.get('phone') and client.phone != client_data['phone']:
                        logger.info(f"   Actualizando teléfono: '{client.phone}' -> '{client_data['phone']}'")
                        client.phone = client_data['phone']
                        updated = True
                    if client_data.get('address') and client.address != client_data['address']:
                        client.address = client_data['address']
                        updated = True
                    if client_data.get('city') and client.city != client_data['city']:
                        client.city = client_data['city']
                        updated = True
                    if client_data.get('country') and client.country != client_data['country']:
                        client.country = client_data['country']
                        updated = True
                    
                    if updated:
                        client.save()
                        logger.info(f"   ✅ Cliente actualizado")
                    
                    return client
                except Client.DoesNotExist:
                    logger.info(f"   Cliente no encontrado por email, creando nuevo")
            else:
                logger.info(f"   No se proporcionó email, creando nuevo cliente")
        except Exception as e:
            logger.error(f"   ❌ Error buscando cliente: {str(e)}")
            # Continuar para crear nuevo cliente
        
        # Si no existe, crear nuevo cliente
        logger.info(f"   Creando nuevo cliente con nombre: {client_data.get('name')}")
        new_client = Client.objects.create(
            name=client_data.get('name', 'Cliente'),
            email=client_data.get('email', ''),
            phone=client_data.get('phone', ''),
            address=client_data.get('address', ''),
            city=client_data.get('city', ''),
            country=client_data.get('country', 'México'),
            user=None  # Cliente administrativo
        )
        logger.info(f"   ✅ Nuevo cliente creado: ID={new_client.id}, Nombre={new_client.name}, Email={new_client.email}")
        return new_client


class SaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualizar y eliminar venta"""
    queryset = Sale.objects.select_related('client', 'user').all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_cart(request):
    """Obtener carrito activo del usuario o anónimo"""
    cart = get_or_create_cart(request)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_or_get_cart(request):
    """Crear o obtener carrito del usuario o anónimo"""
    cart = get_or_create_cart(request)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_product_to_cart(request):
    """Agregar producto al carrito del usuario o anónimo"""
    cart = get_or_create_cart(request)
    
    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            from apps.products.models import Product
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar stock disponible
        if product.stock < quantity:
            return Response(
                {'error': 'Stock insuficiente'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Agregar al carrito
        cart_item = cart.add_product(product, quantity)
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sale_from_cart(request, cart_id):
    """Crear venta desde carrito"""
    try:
        cart = Cart.objects.get(id=cart_id, is_active=True)
    except Cart.DoesNotExist:
        return Response({'error': 'Carrito no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    if not cart.items.exists():
        return Response({'error': 'El carrito está vacío'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Crear venta
    sale_data = {
        'client': cart.client,
        'user': request.user,
        'subtotal': cart.total_amount,
        'total': cart.total_amount,
        'status': 'completed',
        'payment_status': 'paid',
        'items': []
    }
    
    # Agregar items de la venta
    for cart_item in cart.items.all():
        sale_data['items'].append({
            'product': cart_item.product,
            'quantity': cart_item.quantity,
            'price': cart_item.price
        })
    
    serializer = CreateSaleSerializer(data=sale_data)
    if serializer.is_valid():
        sale = serializer.save()
        
        # Desactivar carrito
        cart.is_active = False
        cart.save()
        
        # Crear comprobante
        SaleReceipt.objects.create(
            sale=sale,
            receipt_number=f"RCP-{sale.id}",
            qr_code=f"https://smartsales365.com/receipt/{sale.id}"
        )
        
        # Enviar notificación push cuando la venta está completada
        if sale.status == 'completed':
            try:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Venta {sale.id} completada (desde carrito). Enviando notificaciones...")
                from apps.core.services import NotificationService
                result = NotificationService.send_sale_notification(str(sale.id))
                if result:
                    logger.info(f"Notificaciones enviadas exitosamente para venta {sale.id}")
                else:
                    logger.warning(f"Notificaciones retornaron False para venta {sale.id}")
            except Exception as notif_error:
                # No fallar la creación de la venta si hay error en notificaciones
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error enviando notificación de venta {sale.id}: {notif_error}", exc_info=True)
        
        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def checkout_cart(request):
    """Procesar checkout del carrito con información del cliente"""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        return Response({'error': 'El carrito está vacío'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtener información del cliente del request
    # El frontend puede enviar client directamente o client.client (anidado)
    client_data_raw = request.data.get('client', {})
    
    # Si client_data tiene otra propiedad 'client' dentro, usar esa
    # Esto maneja el caso cuando el frontend envía: {client: {client: {...}}}
    if isinstance(client_data_raw, dict) and 'client' in client_data_raw and isinstance(client_data_raw.get('client'), dict):
        client_data = client_data_raw.get('client', {})
    else:
        # Si client_data ya tiene los campos directamente, usarlo
        client_data = client_data_raw
    
    # Extraer todos los campos del cliente que envía el frontend
    client_name = client_data.get('name', '')
    client_email = client_data.get('email', '')
    client_phone = client_data.get('phone', '')
    client_address = client_data.get('address', '')
    client_city = client_data.get('city', '')
    client_country = client_data.get('country', 'Bolivia')
    
    # Debug: Log para ver qué se está recibiendo
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 Datos recibidos en checkout_cart:")
    logger.info(f"   request.data.client: {request.data.get('client')}")
    logger.info(f"   client_data procesado: {client_data}")
    logger.info(f"   client_name extraído: '{client_name}'")
    
    # Validar que se proporcione al menos el nombre
    if not client_name:
        logger.error(f"❌ Error: Nombre del cliente vacío. client_data completo: {client_data}")
        return Response({
            'error': 'El nombre del cliente es requerido',
            'debug': {
                'client_data_received': str(client_data),
                'client_name_extracted': client_name,
                'raw_client_data': str(request.data.get('client'))
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtener método de pago y datos de Stripe
    payment_method = request.data.get('payment_method', 'cash')
    stripe_payment_intent_id = request.data.get('stripe_payment_intent_id', '')
    
    # Crear o obtener cliente
    from apps.clients.models import Client
    from django.db import IntegrityError
    
    client = None
    
    # Si el usuario está autenticado, buscar cliente existente
    if request.user.is_authenticated:
        try:
            client = Client.objects.get(user=request.user)
        except Client.DoesNotExist:
            pass
    
    # Si no se encontró cliente por usuario, buscar por email
    if not client and client_email:
        try:
            client = Client.objects.get(email=client_email)
        except Client.DoesNotExist:
            pass
    
    # Si existe cliente, actualizarlo con los datos del frontend
    if client:
        # Actualizar datos del cliente con la información proporcionada
        client.name = client_name if client_name else client.name
        if client_email:
            client.email = client_email
        if client_phone:
            client.phone = client_phone
        if client_address:
            client.address = client_address
        if client_city:
            client.city = client_city
        if client_country:
            client.country = client_country
        client.save()
    else:
        # Si no existe cliente, crear uno nuevo con todos los datos
        try:
            client = Client.objects.create(
                name=client_name,
                email=client_email if client_email else '',
                phone=client_phone if client_phone else '',
                address=client_address if client_address else '',
                city=client_city if client_city else '',
                country=client_country if client_country else 'Bolivia',
                user=request.user if request.user.is_authenticated else None
            )
        except IntegrityError as e:
            # Si hay conflicto de integridad (email duplicado), obtener el cliente existente
            if client_email:
                try:
                    client = Client.objects.get(email=client_email)
                    # Actualizar con los nuevos datos
                    client.name = client_name if client_name else client.name
                    if client_phone:
                        client.phone = client_phone
                    if client_address:
                        client.address = client_address
                    if client_city:
                        client.city = client_city
                    if client_country:
                        client.country = client_country
                    client.save()
                except Client.DoesNotExist:
                    # Si no existe por email, crear con email diferente o sin email
                    client = Client.objects.create(
                        name=client_name,
                        email='',
                        phone=client_phone if client_phone else '',
                        address=client_address if client_address else '',
                        city=client_city if client_city else '',
                        country=client_country if client_country else 'Bolivia',
                        user=request.user if request.user.is_authenticated else None
                    )
            else:
                raise e
    
    # Crear venta
    sale_data = {
        'client': client.id,
        'user': request.user.id if request.user.is_authenticated else None,
        'subtotal': float(cart.total_amount),
        'total': float(cart.total_amount),
        'status': 'completed',
        'payment_status': 'paid',
        'transaction_id': stripe_payment_intent_id if payment_method == 'stripe' else '',
        'items': []
    }
    
    # Agregar items de la venta
    for cart_item in cart.items.all():
        sale_data['items'].append({
            'product': cart_item.product.id,
            'quantity': cart_item.quantity,
            'price': float(cart_item.price)
        })
    
    serializer = CreateSaleSerializer(data=sale_data)
    if serializer.is_valid():
        sale = serializer.save()
        
        # Actualizar stock de productos
        for cart_item in cart.items.all():
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Desactivar carrito
        cart.is_active = False
        cart.save()
        
        # Crear comprobante
        SaleReceipt.objects.create(
            sale=sale,
            receipt_number=f"RCP-{sale.id}",
            qr_code=f"https://smartsales365.com/receipt/{sale.id}"
        )
        
        # Enviar notificación push cuando la venta está completada
        if sale.status == 'completed':
            try:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Venta {sale.id} completada (checkout). Enviando notificaciones...")
                from apps.core.services import NotificationService
                result = NotificationService.send_sale_notification(str(sale.id))
                if result:
                    logger.info(f"Notificaciones enviadas exitosamente para venta {sale.id}")
                else:
                    logger.warning(f"Notificaciones retornaron False para venta {sale.id}")
            except Exception as notif_error:
                # No fallar la creación de la venta si hay error en notificaciones
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error enviando notificación de venta {sale.id}: {notif_error}", exc_info=True)
        
        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sale_stats(request):
    """Estadísticas de ventas"""
    today = timezone.now().date()
    
    stats = Sale.objects.aggregate(
        total_sales=Count('id'),
        completed_sales=Count('id', filter=Q(status='completed')),
        pending_sales=Count('id', filter=Q(status='pending')),
        cancelled_sales=Count('id', filter=Q(status='cancelled')),
        total_revenue=Sum('total', filter=Q(status='completed')),
        average_sale=Avg('total', filter=Q(status='completed')),
        today_sales=Count('id', filter=Q(created_at__date=today, status='completed')),
        today_revenue=Sum('total', filter=Q(created_at__date=today, status='completed'))
    )
    
    serializer = SaleStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_by_period(request):
    """Ventas por período"""
    period = request.GET.get('period', 'week')  # week, month, year
    
    if period == 'week':
        start_date = timezone.now() - timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now() - timedelta(days=30)
    elif period == 'year':
        start_date = timezone.now() - timedelta(days=365)
    else:
        start_date = timezone.now() - timedelta(days=7)
    
    sales = Sale.objects.filter(
        created_at__gte=start_date,
        status='completed'
    ).order_by('created_at')
    
    serializer = SaleSerializer(sales, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_products(request):
    """Productos más vendidos"""
    from django.db.models import Sum
    
    top_products = SaleItem.objects.filter(
        sale__status='completed'
    ).values(
        'product__name', 'product__sku'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('subtotal')
    ).order_by('-total_sold')[:10]
    
    return Response(top_products)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_public_sales(request):
    """Obtener ventas realizadas desde la tienda pública"""
    try:
        # Obtener ventas donde el usuario es None (ventas públicas)
        public_sales = Sale.objects.filter(
            user__isnull=True,
            status='completed'
        ).select_related('client').prefetch_related('items__product').order_by('-created_at')
        
        # Aplicar filtros si se proporcionan
        status_filter = request.GET.get('status')
        if status_filter:
            public_sales = public_sales.filter(status=status_filter)
        
        date_from = request.GET.get('date_from')
        if date_from:
            public_sales = public_sales.filter(created_at__date__gte=date_from)
        
        date_to = request.GET.get('date_to')
        if date_to:
            public_sales = public_sales.filter(created_at__date__lte=date_to)
        
        # Paginación
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        sales_data = public_sales[start:end]
        total_count = public_sales.count()
        
        serializer = SaleSerializer(sales_data, many=True)
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sales_summary(request):
    """Obtener resumen de ventas (públicas y administrativas)"""
    try:
        from django.db.models import Count, Sum, Q
        from datetime import datetime, timedelta
        
        # Ventas públicas (user is null)
        public_sales = Sale.objects.filter(user__isnull=True, status='completed')
        
        # Ventas administrativas (user is not null)
        admin_sales = Sale.objects.filter(user__isnull=False, status='completed')
        
        # Estadísticas generales
        total_public_sales = public_sales.count()
        total_admin_sales = admin_sales.count()
        total_public_revenue = public_sales.aggregate(Sum('total'))['total__sum'] or 0
        total_admin_revenue = admin_sales.aggregate(Sum('total'))['total__sum'] or 0
        
        # Ventas de hoy
        today = datetime.now().date()
        today_public = public_sales.filter(created_at__date=today).count()
        today_admin = admin_sales.filter(created_at__date=today).count()
        today_public_revenue = public_sales.filter(created_at__date=today).aggregate(Sum('total'))['total__sum'] or 0
        today_admin_revenue = admin_sales.filter(created_at__date=today).aggregate(Sum('total'))['total__sum'] or 0
        
        # Ventas de esta semana
        week_start = today - timedelta(days=today.weekday())
        week_public = public_sales.filter(created_at__date__gte=week_start).count()
        week_admin = admin_sales.filter(created_at__date__gte=week_start).count()
        week_public_revenue = public_sales.filter(created_at__date__gte=week_start).aggregate(Sum('total'))['total__sum'] or 0
        week_admin_revenue = admin_sales.filter(created_at__date__gte=week_start).aggregate(Sum('total'))['total__sum'] or 0
        
        return Response({
            'public_sales': {
                'total_sales': total_public_sales,
                'total_revenue': float(total_public_revenue),
                'today_sales': today_public,
                'today_revenue': float(today_public_revenue),
                'week_sales': week_public,
                'week_revenue': float(week_public_revenue)
            },
            'admin_sales': {
                'total_sales': total_admin_sales,
                'total_revenue': float(total_admin_revenue),
                'today_sales': today_admin,
                'today_revenue': float(today_admin_revenue),
                'week_sales': week_admin,
                'week_revenue': float(week_admin_revenue)
            },
            'combined': {
                'total_sales': total_public_sales + total_admin_sales,
                'total_revenue': float(total_public_revenue + total_admin_revenue),
                'today_sales': today_public + today_admin,
                'today_revenue': float(today_public_revenue + today_admin_revenue),
                'week_sales': week_public + week_admin,
                'week_revenue': float(week_public_revenue + week_admin_revenue)
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)