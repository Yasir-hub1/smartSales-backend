from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Category, Product, PriceHistory
from .serializers import (
    CategorySerializer, ProductSerializer, ProductListSerializer,
    PriceHistorySerializer, ProductStockUpdateSerializer
)


class CategoryListCreateView(generics.ListCreateAPIView):
    """Listar y crear categorías"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualizar y eliminar categoría"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class ProductListCreateView(generics.ListCreateAPIView):
    """Listar y crear productos"""
    queryset = Product.objects.select_related('category').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'category', 'is_digital']
    search_fields = ['name', 'sku', 'description', 'barcode']
    ordering_fields = ['name', 'price', 'stock', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros adicionales
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        stock_status = self.request.query_params.get('stock_status')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if stock_status:
            if stock_status == 'low_stock':
                queryset = queryset.filter(stock__lte=models.F('min_stock'))
            elif stock_status == 'out_of_stock':
                queryset = queryset.filter(stock=0)
            elif stock_status == 'in_stock':
                queryset = queryset.filter(stock__gt=models.F('min_stock'))
        
        return queryset


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualizar y eliminar producto"""
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        """Registrar cambio de precio si es necesario"""
        instance = serializer.instance
        old_price = instance.price
        
        serializer.save()
        
        # Si el precio cambió, registrar en historial
        if old_price != serializer.instance.price:
            PriceHistory.objects.create(
                product=serializer.instance,
                old_price=old_price,
                new_price=serializer.instance.price,
                change_reason='Actualización manual'
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_product_stock(request, pk):
    """Actualizar stock de un producto"""
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductStockUpdateSerializer(data=request.data)
    if serializer.is_valid():
        quantity = serializer.validated_data['quantity']
        operation = serializer.validated_data['operation']
        reason = serializer.validated_data.get('reason', 'Actualización de stock')
        
        if operation == 'add':
            product.stock += quantity
        elif operation == 'subtract':
            if product.stock < quantity:
                return Response(
                    {'error': 'No hay suficiente stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            product.stock -= quantity
        elif operation == 'set':
            product.stock = quantity
        
        product.save()
        
        return Response({
            'message': 'Stock actualizado exitosamente',
            'new_stock': product.stock
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_price_history(request, pk):
    """Obtener historial de precios de un producto"""
    try:
        product = Product.objects.get(pk=pk)
        history = PriceHistory.objects.filter(product=product).order_by('-created_at')
        serializer = PriceHistorySerializer(history, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def low_stock_products(request):
    """Obtener productos con stock bajo"""
    products = Product.objects.filter(
        stock__lte=models.F('min_stock'),
        is_active=True
    ).select_related('category')
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_stats(request):
    """Estadísticas de productos"""
    from django.db.models import Count, Sum, Avg
    
    stats = {
        'total_products': Product.objects.filter(is_active=True).count(),
        'low_stock_count': Product.objects.filter(
            stock__lte=models.F('min_stock'),
            is_active=True
        ).count(),
        'out_of_stock_count': Product.objects.filter(stock=0, is_active=True).count(),
        'total_value': Product.objects.filter(is_active=True).aggregate(
            total=Sum(models.F('stock') * models.F('price'))
        )['total'] or 0,
        'average_price': Product.objects.filter(is_active=True).aggregate(
            avg=Avg('price')
        )['avg'] or 0,
        'categories_count': Category.objects.filter(is_active=True).count()
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_products(request):
    """Búsqueda avanzada de productos"""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    queryset = Product.objects.filter(is_active=True).select_related('category')
    
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(description__icontains=query) |
            Q(barcode__icontains=query)
        )
    
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    
    serializer = ProductListSerializer(queryset, many=True)
    return Response(serializer.data)