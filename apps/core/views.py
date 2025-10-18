from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from .models import User

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Endpoint de verificación de salud del servidor"""
    return Response({
        'status': 'ok',
        'message': 'Servidor funcionando correctamente',
        'timestamp': timezone.now().isoformat()
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Endpoint básico de estadísticas del dashboard"""
    try:
        # Estadísticas básicas (por ahora con datos mock)
        stats = {
            'total_products': 0,
            'total_clients': 0,
            'total_sales': 0,
            'total_revenue': 0.0,
            'recent_sales': [],
            'top_products': [],
            'monthly_revenue': []
        }
        
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Error obteniendo estadísticas del dashboard',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)