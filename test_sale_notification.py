#!/usr/bin/env python
"""
Script para probar el envío de notificaciones cuando se crea una venta
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.sales.models import Sale, SaleItem, Client
from apps.products.models import Product
from apps.core.models import User
from apps.mobile.models import PushNotificationDevice
from apps.core.services import NotificationService
from django.utils import timezone
from decimal import Decimal

def test_sale_notification():
    """Crear una venta de prueba y verificar que se envía la notificación"""
    
    print("🧪 Iniciando prueba de notificación de venta...")
    print("=" * 60)
    
    # 1. Verificar que hay un usuario admin
    try:
        admin = User.objects.filter(is_staff=True).first()
        if not admin:
            print("❌ No hay usuarios administradores en el sistema")
            print("💡 Crea un superusuario: python manage.py createsuperuser")
            return False
        print(f"✅ Usuario admin encontrado: {admin.username}")
    except Exception as e:
        print(f"❌ Error obteniendo usuario admin: {e}")
        return False
    
    # 2. Verificar que hay dispositivos registrados
    devices = PushNotificationDevice.objects.filter(user=admin, is_active=True)
    device_count = devices.count()
    
    if device_count == 0:
        print(f"⚠️  No hay dispositivos registrados para el usuario {admin.username}")
        print("💡 Abre la app móvil e inicia sesión para registrar un dispositivo")
        print(f"📱 Usuario: {admin.username}")
        return False
    
    print(f"✅ {device_count} dispositivo(s) registrado(s) para {admin.username}")
    for device in devices:
        print(f"   - {device.device_type}: {device.device_token[:30]}...")
    
    # 3. Verificar que hay productos
    products = Product.objects.filter(is_active=True)[:3]
    if products.count() == 0:
        print("❌ No hay productos en el sistema")
        print("💡 Crea algunos productos primero")
        return False
    
    print(f"✅ {products.count()} producto(s) encontrado(s)")
    
    # 4. Obtener o crear un cliente de prueba
    client, created = Client.objects.get_or_create(
        email='cliente_test@example.com',
        defaults={
            'name': 'Cliente de Prueba',
            'phone': '1234567890',
        }
    )
    if created:
        print(f"✅ Cliente de prueba creado: {client.name}")
    else:
        print(f"✅ Cliente de prueba existente: {client.name}")
    
    # 5. Crear una venta de prueba
    print("\n📦 Creando venta de prueba...")
    try:
        sale = Sale.objects.create(
            client=client,
            user=admin,
            subtotal=Decimal('100.00'),
            discount=Decimal('0.00'),
            total=Decimal('100.00'),
            status='completed',
            payment_status='paid',
            notes='Venta de prueba para notificaciones'
        )
        
        # Agregar items a la venta
        total_items = 0
        for product in products:
            quantity = 1
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price=product.price
            )
            total_items += quantity
            # Actualizar stock
            product.stock -= quantity
            product.save()
        
        print(f"✅ Venta creada exitosamente:")
        print(f"   - ID: {sale.id}")
        print(f"   - Cliente: {sale.client.name}")
        print(f"   - Total: ${sale.total}")
        print(f"   - Items: {total_items}")
        
    except Exception as e:
        print(f"❌ Error creando venta: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Enviar notificación manualmente
    print("\n📤 Enviando notificación push...")
    try:
        result = NotificationService.send_sale_notification(str(sale.id))
        
        if result:
            print("✅ Notificación enviada exitosamente")
            
            # Verificar que se crearon notificaciones en BD
            from apps.notifications.models import Notification
            notifications = Notification.objects.filter(
                user=admin,
                title__icontains='Nueva Venta',
                created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
            )
            
            if notifications.exists():
                print(f"✅ {notifications.count()} notificación(es) creada(s) en la base de datos")
                for notif in notifications:
                    print(f"   - {notif.title}: {notif.message[:50]}...")
            else:
                print("⚠️  No se encontraron notificaciones en BD (puede ser normal si hubo error)")
        else:
            print("⚠️  La función retornó False (revisa los logs)")
            
    except Exception as e:
        print(f"❌ Error enviando notificación: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada!")
    print(f"📱 Revisa tu app móvil para ver la notificación")
    print(f"🔍 También revisa: http://localhost:8000/admin/mobile/pushnotificationdevice/")
    
    return True

if __name__ == '__main__':
    success = test_sale_notification()
    sys.exit(0 if success else 1)

