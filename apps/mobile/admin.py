from django.contrib import admin
from .models import PushNotificationDevice


@admin.register(PushNotificationDevice)
class PushNotificationDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_type', 'device_token', 'is_active', 'last_notification_sent', 'created_at']
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'device_token', 'device_id']
    readonly_fields = ['created_at', 'updated_at', 'last_notification_sent']

