from django.db import models
from django.conf import settings
from apps.core.models import BaseModel


class PushNotificationDevice(BaseModel):
    """Dispositivos registrados para recibir notificaciones push"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    device_token = models.CharField(max_length=255, unique=True, verbose_name='Token del Dispositivo')
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('ios', 'iOS'),
            ('android', 'Android'),
            ('web', 'Web')
        ],
        default='android',
        verbose_name='Tipo de Dispositivo'
    )
    device_id = models.CharField(max_length=255, blank=True, verbose_name='ID del Dispositivo')
    app_version = models.CharField(max_length=50, blank=True, verbose_name='Versión de la App')
    # is_active ya está heredado de BaseModel
    last_notification_sent = models.DateTimeField(null=True, blank=True, verbose_name='Última Notificación Enviada')
    
    class Meta:
        verbose_name = 'Dispositivo Push'
        verbose_name_plural = 'Dispositivos Push'
        unique_together = [['user', 'device_token']]
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type}"

