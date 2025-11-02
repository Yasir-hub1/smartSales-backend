#!/usr/bin/env python
"""
Script para verificar la configuración de PostgreSQL y usuarios/tablas
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from apps.mobile.models import PushNotificationDevice
from apps.notifications.models import Notification
from apps.core.models import User

def check_database():
    """Verificar conexión y estructura de base de datos"""
    print("🔍 Verificando configuración de PostgreSQL...")
    print("=" * 60)
    
    # 1. Verificar conexión
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL conectado: {version.split(',')[0]}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # 2. Verificar tabla de usuarios
    print("\n👥 USUARIOS:")
    try:
        User = get_user_model()
        users = User.objects.all()
        admin_users = User.objects.filter(is_staff=True, is_superuser=True)
        staff_users = User.objects.filter(is_staff=True)
        
        print(f"   Total usuarios: {users.count()}")
        print(f"   Superusuarios: {admin_users.count()}")
        print(f"   Staff (admin): {staff_users.count()}")
        
        if users.exists():
            print("\n   Lista de usuarios:")
            for user in users:
                roles = []
                if user.is_superuser:
                    roles.append("Superadmin")
                if user.is_staff:
                    roles.append("Admin")
                if not roles:
                    roles.append("Usuario")
                
                print(f"   - {user.username} ({user.email or 'Sin email'}) - {', '.join(roles)}")
        else:
            print("   ⚠️  No hay usuarios en la base de datos")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Verificar tablas de notificaciones
    print("\n📬 TABLAS DE NOTIFICACIONES:")
    
    # Tabla notifications_notification
    try:
        notifications = Notification.objects.all()
        unread = Notification.objects.filter(is_read=False)
        print(f"   ✅ notifications_notification existe")
        print(f"      Total: {notifications.count()}")
        print(f"      No leídas: {unread.count()}")
    except Exception as e:
        print(f"   ❌ notifications_notification: {e}")
    
    # Tabla mobile_pushnotificationdevice
    try:
        devices = PushNotificationDevice.objects.all()
        active_devices = PushNotificationDevice.objects.filter(is_active=True)
        print(f"   ✅ mobile_pushnotificationdevice existe")
        print(f"      Total dispositivos: {devices.count()}")
        print(f"      Dispositivos activos: {active_devices.count()}")
        
        if devices.exists():
            print("\n   Dispositivos registrados:")
            for device in devices[:5]:
                status = "🟢 Activo" if device.is_active else "🔴 Inactivo"
                print(f"   - {device.device_type.upper()}: {device.device_token[:30]}... ({status})")
    except Exception as e:
        print(f"   ❌ mobile_pushnotificationdevice: {e}")
    
    # 4. Verificar otras tablas importantes
    print("\n📊 OTRAS TABLAS:")
    try:
        from apps.sales.models import Sale
        from apps.products.models import Product
        from apps.clients.models import Client
        
        sales = Sale.objects.all()
        products = Product.objects.all()
        clients = Client.objects.all()
        
        print(f"   ✅ sales_sale: {sales.count()} ventas")
        print(f"   ✅ products_product: {products.count()} productos")
        print(f"   ✅ clients_client: {clients.count()} clientes")
        
    except Exception as e:
        print(f"   ❌ Error verificando otras tablas: {e}")
    
    # 5. Verificar todas las tablas en la base de datos
    print("\n📋 TODAS LAS TABLAS EN LA BASE DE DATOS:")
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"   Total: {len(tables)} tablas")
            
            # Filtrar tablas importantes
            important_tables = [
                'core_user',
                'notifications_notification',
                'mobile_pushnotificationdevice',
                'sales_sale',
                'products_product',
                'clients_client',
            ]
            
            found_important = []
            for table in tables:
                table_name = table[0]
                if any(important in table_name for important in important_tables):
                    found_important.append(table_name)
                    print(f"   ✅ {table_name}")
            
            missing = [t for t in important_tables if not any(t in f for f in found_important)]
            if missing:
                print(f"\n   ⚠️  Tablas faltantes esperadas: {missing}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Verificación completada")
    
    return True

if __name__ == '__main__':
    check_database()

