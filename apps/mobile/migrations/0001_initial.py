# Generated migration for PushNotificationDevice model
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotificationDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('device_token', models.CharField(max_length=255, unique=True, verbose_name='Token del Dispositivo')),
                ('device_type', models.CharField(choices=[('ios', 'iOS'), ('android', 'Android'), ('web', 'Web')], default='android', max_length=20, verbose_name='Tipo de Dispositivo')),
                ('device_id', models.CharField(blank=True, max_length=255, verbose_name='ID del Dispositivo')),
                ('app_version', models.CharField(blank=True, max_length=50, verbose_name='Versión de la App')),
                ('last_notification_sent', models.DateTimeField(blank=True, null=True, verbose_name='Última Notificación Enviada')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Dispositivo Push',
                'verbose_name_plural': 'Dispositivos Push',
                'unique_together': {('user', 'device_token')},
            },
        ),
    ]

