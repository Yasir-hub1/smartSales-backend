from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Notification(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    title = models.CharField(max_length=200, verbose_name='Título')
    message = models.TextField(verbose_name='Mensaje')
    notification_type = models.CharField(max_length=50, choices=[
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('success', 'Éxito'),
        ('error', 'Error')
    ], default='info', verbose_name='Tipo')
    is_read = models.BooleanField(default=False, verbose_name='Leída')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Leída en')
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
