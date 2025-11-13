#!/usr/bin/env python
"""
Script para probar el flujo completo de notificaciones al crear una venta
"""
import os
import sys
import django
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

from apps.sales.models import Sale, SaleItem
from apps.products.models import Product
from apps.clients.models import Client
from apps.core.models import User
from apps.notifications.models import Notification
from apps.mobile.models import PushNotificationDevice
from apps.core.services import NotificationService
from decimal import Decimal
from django.utils import timezone

def test_notification_flow():
    """Probar el flujo completo de notificaciones"""
    
    print("🧪 Probando flujo completo de notificaciones...")
    print("=" * 60)
    
    # 1. Verificar usuarios admin
    admins = User.objects.filter(is_staff=True)
    print(f"\n1️⃣ Usuarios admin encontrados: {admins.count()}")
    for admin in admins:
        print(f"   - {admin.username} (ID: {admin.id})")
    
    if admins.count() == 0:
        print("❌ No hay usuarios admin. No se pueden enviar notificaciones.")
        return False
    
    # 2. Verificar dispositivos registrados
    print(f"\n2️⃣ Dispositivos registrados:")
    total_devices = 0
    for admin in admins:
        devices = PushNotificationDevice.objects.filter(user=admin, is_active=True)
        print(f"   {admin.username}: {devices.count()} dispositivo(s) activo(s)")
        for device in devices:
            print(f"      - {device.device_type}: {device.device_token[:40]}...")
            total_devices += 1
    
    if total_devices == 0:
        print("⚠️  ADVERTENCIA: No hay dispositivos registrados.")
        print("   La notificación se creará en BD pero NO se enviará push.")
        print("   Para recibir push, registra un dispositivo desde la app móvil.")
    else:
        print(f"✅ Total: {total_devices} dispositivo(s) listo(s) para recibir notificaciones")
    
    # 3. Obtener productos
    products = Product.objects.filter(is_active=True)[:2]
    if products.count() < 1:
        print("\n❌ No hay productos disponibles")
        return False
    
    print(f"\n3️⃣ Productos disponibles: {products.count()}")
    
    # 4. Obtener o crear cliente
    client, _ = Client.objects.get_or_create(
        email='test_notif@example.com',
        defaults={'name': 'Cliente Test Notificaciones', 'phone': '1234567890'}
    )
    print(f"4️⃣ Cliente: {client.name}")
    
    # 5. Crear venta
    print(f"\n5️⃣ Creando venta de prueba...")
    try:
        sale = Sale.objects.create(
            client=client,
            user=admins.first(),
            subtotal=Decimal('200.00'),
            discount=Decimal('0.00'),
            total=Decimal('200.00'),
            status='completed',
            payment_status='paid',
            notes='Venta de prueba para notificaciones'
        )
        
        # Agregar items (solo productos con stock disponible)
        for product in products:
            quantity = min(1, product.stock)  # Solo tomar lo que hay disponible
            if quantity > 0:
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                product.stock -= quantity
                product.save()
        
        print(f"   ✅ Venta creada: ID={sale.id}, Total=${sale.total}")
        
    except Exception as e:
        print(f"   ❌ Error creando venta: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Llamar directamente a NotificationService
    print(f"\n6️⃣ Enviando notificación (simulando flujo real)...")
    try:
        result = NotificationService.send_sale_notification(str(sale.id))
        
        if result:
            print("   ✅ NotificationService retornó True")
        else:
            print("   ⚠️  NotificationService retornó False")
            
    except Exception as e:
        print(f"   ❌ Error en NotificationService: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. Verificar notificaciones en BD
    print(f"\n7️⃣ Verificando notificaciones en base de datos...")
    notifications = Notification.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
    ).order_by('-created_at')
    
    print(f"   Total notificaciones creadas en último minuto: {notifications.count()}")
    
    for notif in notifications[:5]:
        print(f"   - {notif.title}")
        print(f"     Para: {notif.user.username}")
        print(f"     Mensaje: {notif.message[:60]}...")
        print(f"     Tipo: {notif.notification_type}")
        print(f"     Leída: {notif.is_read}")
        print()
    
    # 8. Verificar dispositivos y último envío
    print(f"\n8️⃣ Verificando dispositivos y último envío...")
    for admin in admins:
        devices = PushNotificationDevice.objects.filter(user=admin, is_active=True)
        for device in devices:
            last_sent = device.last_notification_sent
            if last_sent:
                time_diff = timezone.now() - last_sent
                print(f"   {device.device_type} ({admin.username}):")
                print(f"      Último envío: {last_sent}")
                print(f"      Hace: {time_diff.total_seconds():.0f} segundos")
            else:
                print(f"   {device.device_type} ({admin.username}): Nunca se ha enviado")
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada")
    
    return True

if __name__ == '__main__':
    test_notification_flow()

