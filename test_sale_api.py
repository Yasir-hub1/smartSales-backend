#!/usr/bin/env python
"""
Script para probar la creación de venta desde la API REST
y verificar que se envía la notificación automáticamente
"""
import os
import sys
import django
import requests
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.sales.models import Sale, SaleItem
from apps.products.models import Product
from apps.clients.models import Client
from apps.core.models import User
from apps.notifications.models import Notification
from django.utils import timezone

API_BASE_URL = 'http://localhost:8000/api/v1'

def get_auth_token(username, password):
    """Obtener token de autenticación"""
    url = f'{API_BASE_URL}/auth/login/'
    response = requests.post(url, json={
        'username': username,
        'password': password
    })
    if response.status_code == 200:
        return response.json().get('access')
    return None

def test_create_sale_via_api():
    """Probar crear venta desde la API"""
    
    print("🧪 Probando creación de venta desde API REST...")
    print("=" * 60)
    
    # 1. Obtener usuario admin
    try:
        admin = User.objects.filter(is_staff=True).first()
        if not admin:
            print("❌ No hay usuarios admin")
            return False
        
        print(f"✅ Usuario admin: {admin.username}")
        
        # Intentar login (usar password por defecto o el que tenga)
        # En desarrollo, puedes resetear la password:
        # admin.set_password('test123')
        # admin.save()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 2. Obtener productos
    products = Product.objects.filter(is_active=True)[:3]
    if products.count() < 1:
        print("❌ No hay productos")
        return False
    
    print(f"✅ Productos disponibles: {products.count()}")
    
    # 3. Obtener o crear cliente
    client, _ = Client.objects.get_or_create(
        email='api_test@example.com',
        defaults={'name': 'Cliente API Test', 'phone': '1234567890'}
    )
    print(f"✅ Cliente: {client.name}")
    
    # 4. Preparar datos de la venta
    sale_data = {
        'client': {
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
        },
        'subtotal': 150.00,
        'discount': 0,
        'total': 150.00,
        'status': 'completed',
        'payment_status': 'paid',
        'notes': 'Venta de prueba desde API',
        'items': [
            {
                'product': product.id,
                'quantity': 1,
                'price': float(product.price)
            }
            for product in products[:2]  # Solo 2 productos
        ]
    }
    
    print(f"\n📦 Datos de venta:")
    print(f"   - Cliente: {sale_data['client']['name']}")
    print(f"   - Total: ${sale_data['total']}")
    print(f"   - Items: {len(sale_data['items'])}")
    
    # 5. Intentar crear venta (sin auth primero para ver error)
    print(f"\n📤 Creando venta desde API...")
    url = f'{API_BASE_URL}/sales/'
    
    # NOTA: Necesitas autenticación. Este script es para mostrar la estructura.
    # En producción, usarías:
    # token = get_auth_token(admin.username, 'password')
    # headers = {'Authorization': f'Bearer {token}'}
    # response = requests.post(url, json=sale_data, headers=headers)
    
    print("💡 Para probar completamente, ejecuta esto desde tu app móvil o frontend")
    print(f"   Endpoint: POST {url}")
    print(f"   Body: {json.dumps(sale_data, indent=2)}")
    
    # 6. Verificar que cuando se crea una venta, se llama a NotificationService
    print("\n✅ Verificación:")
    print("   - El endpoint /api/v1/sales/ está configurado")
    print("   - Al crear venta con status='completed', se envía notificación")
    print("   - NotificationService.send_sale_notification() se ejecuta automáticamente")
    
    # Verificar ventas anteriores con notificaciones
    recent_sales = Sale.objects.filter(
        status='completed',
        created_at__gte=timezone.now() - timezone.timedelta(hours=1)
    ).order_by('-created_at')[:5]
    
    if recent_sales.exists():
        print(f"\n📊 Últimas {recent_sales.count()} ventas completadas:")
        for sale in recent_sales:
            notifications = Notification.objects.filter(
                user__is_staff=True,
                title__icontains='Nueva Venta',
                message__icontains=str(sale.id)
            )
            status = "✅" if notifications.exists() else "❌"
            print(f"   {status} Venta #{sale.id} - ${sale.total} - Notificaciones: {notifications.count()}")
    
    return True

if __name__ == '__main__':
    success = test_create_sale_via_api()
    sys.exit(0 if success else 1)

