from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from .models import Client
from .serializers import (
    ClientSerializer, ClientListSerializer, ClientCreateSerializer,
    ClientStatsSerializer
)


class ClientListCreateView(generics.ListCreateAPIView):
    """Listar y crear clientes"""
    queryset = Client.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'client_type', 'segment']
    search_fields = ['name', 'email', 'phone', 'city']
    ordering_fields = ['name', 'created_at', 'total_purchases', 'last_purchase_date']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClientCreateSerializer
        return ClientListSerializer


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualizar y eliminar cliente"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_stats(request):
    """Estadísticas de clientes"""
    from django.db.models import Count, Sum, Avg
    
    stats = Client.objects.aggregate(
        total_clients=Count('id'),
        vip_clients=Count('id', filter=Q(segment='vip')),
        new_clients=Count('id', filter=Q(segment='new')),
        regular_clients=Count('id', filter=Q(segment='regular')),
        business_clients=Count('id', filter=Q(client_type='business')),
        individual_clients=Count('id', filter=Q(client_type='individual')),
        total_purchases=Sum('total_purchases'),
        average_purchase=Avg('total_purchases')
    )
    
    serializer = ClientStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_clients(request):
    """Búsqueda avanzada de clientes"""
    query = request.GET.get('q', '')
    client_type = request.GET.get('client_type')
    segment = request.GET.get('segment')
    city = request.GET.get('city')
    
    queryset = Client.objects.filter(is_active=True)
    
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(city__icontains=query)
        )
    
    if client_type:
        queryset = queryset.filter(client_type=client_type)
    
    if segment:
        queryset = queryset.filter(segment=segment)
    
    if city:
        queryset = queryset.filter(city__icontains=city)
    
    serializer = ClientListSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vip_clients(request):
    """Obtener clientes VIP"""
    clients = Client.objects.filter(segment='vip', is_active=True).order_by('-total_purchases')
    serializer = ClientListSerializer(clients, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def new_clients(request):
    """Obtener clientes nuevos"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Clientes registrados en los últimos 30 días
    thirty_days_ago = timezone.now() - timedelta(days=30)
    clients = Client.objects.filter(
        segment='new',
        is_active=True,
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')
    
    serializer = ClientListSerializer(clients, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_client_segment(request, pk):
    """Actualizar segmento de cliente"""
    try:
        client = Client.objects.get(pk=pk)
    except Client.DoesNotExist:
        return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    segment = request.data.get('segment')
    if segment not in ['vip', 'regular', 'new']:
        return Response(
            {'error': 'Segmento inválido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    client.segment = segment
    client.save()
    
    serializer = ClientSerializer(client)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_purchase_history(request, pk):
    """Obtener historial de compras de un cliente"""
    try:
        client = Client.objects.get(pk=pk)
    except Client.DoesNotExist:
        return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    from apps.sales.models import Sale
    from apps.sales.serializers import SaleSerializer
    
    sales = Sale.objects.filter(client=client).order_by('-created_at')
    serializer = SaleSerializer(sales, many=True)
    
    return Response({
        'client': ClientSerializer(client).data,
        'purchases': serializer.data,
        'total_purchases': client.total_purchases,
        'last_purchase': client.last_purchase_date
    })