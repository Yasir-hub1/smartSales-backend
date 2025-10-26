#!/usr/bin/env python
"""
Script para configurar la base de datos PostgreSQL
"""
import os
import sys
import django
from pathlib import Path

# Agregar el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.core.management import execute_from_command_line

def setup_database():
    """Configura la base de datos"""
    print("🚀 Configurando base de datos PostgreSQL para SmartSales365...")
    
    try:
        # Crear migraciones
        print("📝 Creando migraciones...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # Aplicar migraciones
        print("🔄 Aplicando migraciones...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Crear superusuario
        print("👤 Creando superusuario...")
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@SmartSales365.com',
                password='admin123'
            )
            print("✅ Superusuario creado: admin / admin123")
        else:
            print("ℹ️  Superusuario ya existe")
        
        # Crear datos de ejemplo
        print("📊 Creando datos de ejemplo...")
        create_sample_data()
        
        print("🎉 ¡Base de datos configurada exitosamente!")
        print("\n📋 Información de acceso:")
        print("   - Admin: http://localhost:8000/admin/")
        print("   - API Docs: http://localhost:8000/api/docs/")
        print("   - Usuario: admin")
        print("   - Contraseña: admin123")
        
    except Exception as e:
        print(f"❌ Error configurando la base de datos: {e}")
        sys.exit(1)

def create_sample_data():
    """Crea datos de ejemplo"""
    from apps.core.models import Company
    from apps.products.models import Category, Product
    from apps.clients.models import Client
    
    # Crear empresa
    company, created = Company.objects.get_or_create(
        name='SmartSales365 Demo',
        defaults={
            'description': 'Empresa de demostración',
            'email': 'demo@SmartSales365.com',
            'phone': '+52 55 1234 5678',
            'address': 'Ciudad de México, México'
        }
    )
    
    if created:
        print("   ✅ Empresa creada")
    
    # Crear categorías
    categories_data = [
        {'name': 'Electrónicos', 'description': 'Dispositivos electrónicos'},
        {'name': 'Ropa', 'description': 'Vestimenta y accesorios'},
        {'name': 'Hogar', 'description': 'Artículos para el hogar'},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"   ✅ Categoría '{category.name}' creada")
    
    # Crear productos
    products_data = [
        {'name': 'Laptop Dell XPS 13', 'sku': 'LAP001', 'price': 25000, 'cost': 18000, 'stock': 10, 'category': 'Electrónicos'},
        {'name': 'iPhone 15 Pro', 'sku': 'PHN001', 'price': 30000, 'cost': 22000, 'stock': 5, 'category': 'Electrónicos'},
        {'name': 'Camiseta Nike', 'sku': 'CAM001', 'price': 500, 'cost': 300, 'stock': 50, 'category': 'Ropa'},
        {'name': 'Sofá 3 plazas', 'sku': 'SOF001', 'price': 15000, 'cost': 10000, 'stock': 3, 'category': 'Hogar'},
    ]
    
    for prod_data in products_data:
        category = Category.objects.get(name=prod_data['category'])
        product, created = Product.objects.get_or_create(
            sku=prod_data['sku'],
            defaults={
                'name': prod_data['name'],
                'description': f'Descripción de {prod_data["name"]}',
                'price': prod_data['price'],
                'cost': prod_data['cost'],
                'stock': prod_data['stock'],
                'min_stock': 2,
                'category': category
            }
        )
        if created:
            print(f"   ✅ Producto '{product.name}' creado")
    
    # Crear clientes
    clients_data = [
        {'name': 'Juan Pérez', 'email': 'juan@email.com', 'phone': '555-0001', 'segment': 'vip'},
        {'name': 'María García', 'email': 'maria@email.com', 'phone': '555-0002', 'segment': 'regular'},
        {'name': 'Carlos López', 'email': 'carlos@email.com', 'phone': '555-0003', 'segment': 'new'},
    ]
    
    for client_data in clients_data:
        client, created = Client.objects.get_or_create(
            email=client_data['email'],
            defaults={
                'name': client_data['name'],
                'phone': client_data['phone'],
                'segment': client_data['segment'],
                'city': 'Ciudad de México',
                'country': 'México'
            }
        )
        if created:
            print(f"   ✅ Cliente '{client.name}' creado")

if __name__ == '__main__':
    setup_database()
