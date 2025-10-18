from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    """Serializer para clientes"""
    full_address = serializers.ReadOnlyField()
    is_vip = serializers.ReadOnlyField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'city', 'country',
            'postal_code', 'client_type', 'segment', 'birth_date', 'notes',
            'avatar', 'is_active', 'last_purchase_date', 'total_purchases',
            'full_address', 'is_vip', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_purchase_date']


class ClientListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de clientes"""
    is_vip = serializers.ReadOnlyField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'city', 'client_type', 'segment',
            'is_active', 'is_vip', 'total_purchases', 'last_purchase_date'
        ]


class ClientCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear clientes"""
    
    class Meta:
        model = Client
        fields = [
            'name', 'email', 'phone', 'address', 'city', 'country',
            'postal_code', 'client_type', 'segment', 'birth_date', 'notes'
        ]
    
    def validate_email(self, value):
        """Validar que el email sea único"""
        if Client.objects.filter(email=value).exists():
            raise serializers.ValidationError("El email ya está registrado")
        return value


class ClientStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de clientes"""
    total_clients = serializers.IntegerField()
    vip_clients = serializers.IntegerField()
    new_clients = serializers.IntegerField()
    regular_clients = serializers.IntegerField()
    business_clients = serializers.IntegerField()
    individual_clients = serializers.IntegerField()
    total_purchases = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_purchase = serializers.DecimalField(max_digits=10, decimal_places=2)