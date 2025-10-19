from rest_framework import serializers
from .models import Cart, CartItem, Sale, SaleItem, SaleReceipt
from apps.products.models import Product
from apps.clients.models import Client


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer para items del carrito"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_image = serializers.CharField(source='product.image', read_only=True)
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'product_image',
            'quantity', 'price', 'subtotal', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CartSerializer(serializers.ModelSerializer):
    """Serializer para carrito"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'client', 'session_key', 'is_active', 'items',
            'total_items', 'total_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    """Serializer para agregar producto al carrito"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Producto no encontrado o inactivo")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer para actualizar item del carrito"""
    quantity = serializers.IntegerField(min_value=1)


class SaleItemSerializer(serializers.ModelSerializer):
    """Serializer para items de venta"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'quantity', 'price', 'subtotal'
        ]


class CreateSaleItemSerializer(serializers.Serializer):
    """Serializer para crear items de venta"""
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_product(self, value):
        try:
            Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Producto no encontrado o inactivo")
        return value


class SaleSerializer(serializers.ModelSerializer):
    """Serializer para ventas"""
    items = SaleItemSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Sale
        fields = [
            'id', 'client', 'client_name', 'user', 'user_name', 'subtotal',
            'tax', 'discount', 'total', 'status', 'payment_status', 'notes',
            'transaction_id', 'items', 'total_items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateSaleSerializer(serializers.ModelSerializer):
    """Serializer para crear venta"""
    items = CreateSaleItemSerializer(many=True)
    
    class Meta:
        model = Sale
        fields = [
            'client', 'subtotal', 'discount', 'total',
            'status', 'payment_status', 'notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sale = Sale.objects.create(**validated_data)
        
        for item_data in items_data:
            SaleItem.objects.create(
                sale=sale,
                product_id=item_data['product'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
        
        # Actualizar stock de productos
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product'])
            product.stock -= item_data['quantity']
            product.save()
        
        # Actualizar total de compras del cliente
        client = sale.client
        client.total_purchases += sale.total
        client.last_purchase_date = sale.created_at
        client.save()
        
        return sale


class SaleReceiptSerializer(serializers.ModelSerializer):
    """Serializer para comprobantes de venta"""
    sale_data = SaleSerializer(source='sale', read_only=True)
    
    class Meta:
        model = SaleReceipt
        fields = [
            'id', 'sale', 'sale_data', 'receipt_number', 'pdf_file',
            'qr_code', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SaleStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de ventas"""
    total_sales = serializers.IntegerField()
    completed_sales = serializers.IntegerField()
    pending_sales = serializers.IntegerField()
    cancelled_sales = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_sale = serializers.DecimalField(max_digits=10, decimal_places=2)
    today_sales = serializers.IntegerField()
    today_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)