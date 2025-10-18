from rest_framework import serializers
from .models import Category, Product, PriceHistory


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para categorías"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'parent', 'image', 'is_active',
            'created_at', 'updated_at', 'products_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        """Contar productos en la categoría"""
        return obj.product_set.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    """Serializer para productos"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    profit_margin = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'sku', 'price', 'cost', 'stock',
            'min_stock', 'max_stock', 'category', 'category_name', 'image',
            'is_digital', 'weight', 'dimensions', 'barcode', 'tags',
            'is_active', 'profit_margin', 'is_low_stock', 'stock_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_sku(self, value):
        """Validar que el SKU sea único"""
        if self.instance and self.instance.sku == value:
            return value
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("El SKU ya existe")
        return value
    
    def validate_stock(self, value):
        """Validar stock"""
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo")
        return value
    
    def validate_price(self, value):
        """Validar precio"""
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de productos"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'price', 'stock', 'category_name',
            'stock_status', 'image', 'is_active'
        ]


class PriceHistorySerializer(serializers.ModelSerializer):
    """Serializer para historial de precios"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = PriceHistory
        fields = [
            'id', 'product', 'product_name', 'old_price', 'new_price',
            'change_reason', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductStockUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar stock"""
    quantity = serializers.IntegerField()
    operation = serializers.ChoiceField(choices=['add', 'subtract', 'set'])
    reason = serializers.CharField(max_length=200, required=False)
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa")
        return value