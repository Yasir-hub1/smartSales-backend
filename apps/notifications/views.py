from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.filter(is_active=True)
    
    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user, is_active=True)
        
        # Filtrar por is_read si se proporciona
        is_read_param = self.request.query_params.get('is_read', None)
        if is_read_param is not None:
            is_read_value = is_read_param.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_read=is_read_value)
        
        return queryset
    
    @action(detail=True, methods=['patch', 'post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(is_read=True, read_at=timezone.now())
        return Response({'status': 'all marked as read'})
