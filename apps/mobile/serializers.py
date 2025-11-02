from rest_framework import serializers
from apps.mobile.models import PushNotificationDevice
from apps.products.models import Product
from apps.clients.models import Client
from apps.sales.models import Sale


class MobileLoginSerializer(serializers.Serializer):
    """Serializer para login móvil"""
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False, write_only=True)
    
    def validate(self, attrs):
        from django.contrib.auth import authenticate
        import logging
        logger = logging.getLogger(__name__)
        
        username = attrs.get('username', '').strip()
        password = attrs.get('password', '').strip()
        
        logger.info(f"Validating login for username: {username}")
        
        if not username:
            raise serializers.ValidationError({'username': 'El usuario es requerido'})
        
        if not password:
            raise serializers.ValidationError({'password': 'La contraseña es requerida'})
        
        # Intentar autenticación
        user = authenticate(username=username, password=password)
        
        if not user:
            logger.warning(f"Authentication failed for username: {username}")
            raise serializers.ValidationError({'non_field_errors': ['Credenciales inválidas']})
        
        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {username}")
            raise serializers.ValidationError({'non_field_errors': ['Usuario inactivo']})
        
        attrs['user'] = user
        return attrs


class PushNotificationDeviceSerializer(serializers.ModelSerializer):
    """Serializer para dispositivos de notificaciones push"""
    
    class Meta:
        model = PushNotificationDevice
        fields = [
            'id', 'device_token', 'device_type', 'device_id',
            'app_version', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RegisterDeviceSerializer(serializers.Serializer):
    """Serializer para registrar dispositivo"""
    device_token = serializers.CharField(max_length=255)
    device_type = serializers.ChoiceField(choices=['ios', 'android', 'web'], default='android')
    device_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    app_version = serializers.CharField(max_length=50, required=False, allow_blank=True)


class ProductDashboardSerializer(serializers.ModelSerializer):
    """Serializer para dashboard de productos"""
    category_name = serializers.SerializerMethodField()
    stock_status = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'price', 'stock', 'min_stock', 'max_stock',
            'category_name', 'image', 'stock_status', 'is_low_stock', 'is_active'
        ]
    
    def get_category_name(self, obj):
        """Obtener nombre de categoría de forma segura"""
        return obj.category.name if obj.category else 'Sin categoría'


class ProductDashboardStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del dashboard de productos"""
    total_products = serializers.IntegerField()
    low_stock_products = serializers.IntegerField()
    out_of_stock_products = serializers.IntegerField()
    total_stock_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    categories_count = serializers.IntegerField()


class FrequentClientSerializer(serializers.ModelSerializer):
    """Serializer para clientes frecuentes"""
    purchase_count = serializers.IntegerField(default=0)
    total_spent = serializers.SerializerMethodField()
    last_purchase_date = serializers.SerializerMethodField()  # Cambiar a SerializerMethodField
    is_vip = serializers.ReadOnlyField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'city', 'segment',
            'purchase_count', 'total_spent', 'last_purchase_date', 'is_vip', 'total_purchases'
        ]
    
    def get_total_spent(self, obj):
        """Obtener total gastado de forma segura"""
        if hasattr(obj, 'total_spent') and obj.total_spent:
            return float(obj.total_spent)
        # Si no tiene total_spent calculado, usar total_purchases
        return float(obj.total_purchases) if obj.total_purchases else 0.0
    
    def get_last_purchase_date(self, obj):
        """Obtener fecha de última compra - prioriza anotación, luego campo del modelo"""
        # Primero intentar obtener de la anotación last_sale_date
        if hasattr(obj, 'last_sale_date') and obj.last_sale_date:
            return obj.last_sale_date
        # Si no, usar el campo del modelo
        return obj.last_purchase_date


class ExcelImportSerializer(serializers.Serializer):
    """Serializer para importación de Excel"""
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Validar que el archivo sea Excel"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Log para debugging
        logger.info(f'Validando archivo: name={value.name}, size={value.size}, content_type={getattr(value, "content_type", "N/A")}')
        
        # Verificar nombre del archivo
        file_name = value.name.lower() if value.name else ''
        
        # Verificar extensión
        if not file_name.endswith(('.xlsx', '.xls')):
            logger.error(f'Archivo rechazado por extensión: {file_name}')
            raise serializers.ValidationError(
                f"El archivo debe ser Excel (.xlsx o .xls). Archivo recibido: {value.name}"
            )
        
        # Verificar que el archivo no esté vacío
        if value.size == 0:
            logger.error(f'Archivo vacío rechazado: {value.name}')
            raise serializers.ValidationError("El archivo está vacío o no se envió correctamente")
        
        # Verificar tamaño máximo
        if value.size > 10 * 1024 * 1024:  # 10MB
            logger.error(f'Archivo demasiado grande: {value.name}, tamaño: {value.size} bytes')
            raise serializers.ValidationError("El archivo es demasiado grande (máximo 10MB)")
        
        return value


class ExcelImportResultSerializer(serializers.Serializer):
    """Serializer para resultado de importación"""
    total_rows = serializers.IntegerField()
    successful = serializers.IntegerField()
    failed = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.CharField())

