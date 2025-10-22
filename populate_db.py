#!/usr/bin/env python
"""
Script para poblar la base de datos con datos básicos
"""
import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.core.models import User, Company
from apps.products.models import Product, Category
from apps.clients.models import Client
from apps.sales.models import Sale, SaleItem
from django.utils import timezone
from datetime import datetime, timedelta
import random

def create_basic_data():
    print("Creando datos básicos...")
    
    # Crear empresa
    company, created = Company.objects.get_or_create(
        name='SmartSales365',
        defaults={
            'legal_name': 'SmartSales365 S.A. de C.V.',
            'rfc': 'SSA123456789',
            'address': 'Av. Tecnología 123, Col. Digital, CDMX',
            'phone': '+52 55 1234 5678',
            'email': 'info@smartsales365.com',
            'website': 'https://smartsales365.com'
        }
    )
    print(f"Empresa: {'Creada' if created else 'Ya existe'}")
    
    # Crear categorías
    categories_data = [
        {'name': 'Electrónicos', 'description': 'Dispositivos electrónicos'},
        {'name': 'Ropa', 'description': 'Ropa y accesorios'},
        {'name': 'Hogar', 'description': 'Artículos para el hogar'},
        {'name': 'Deportes', 'description': 'Artículos deportivos'},
        {'name': 'Libros', 'description': 'Libros y material educativo'}
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        categories.append(category)
        print(f"Categoría {category.name}: {'Creada' if created else 'Ya existe'}")
    
    # Crear productos
    products_data = [
        {'name': 'iPhone 15', 'sku': 'IPH15-001', 'price': 15000, 'cost': 12000, 'stock': 50, 'category': 'Electrónicos'},
        {'name': 'Samsung Galaxy S24', 'sku': 'SGS24-001', 'price': 12000, 'cost': 9000, 'stock': 30, 'category': 'Electrónicos'},
        {'name': 'Laptop Dell XPS', 'sku': 'DELL-XPS', 'price': 25000, 'cost': 20000, 'stock': 20, 'category': 'Electrónicos'},
        {'name': 'Camiseta Nike', 'sku': 'NIKE-TSH', 'price': 500, 'cost': 300, 'stock': 100, 'category': 'Ropa'},
        {'name': 'Pantalón Levis', 'sku': 'LEVI-501', 'price': 800, 'cost': 500, 'stock': 80, 'category': 'Ropa'},
        {'name': 'Sofá 3 plazas', 'sku': 'SOFA-3P', 'price': 8000, 'cost': 6000, 'stock': 10, 'category': 'Hogar'},
        {'name': 'Mesa de centro', 'sku': 'MESA-C', 'price': 2000, 'cost': 1500, 'stock': 15, 'category': 'Hogar'},
        {'name': 'Balón de fútbol', 'sku': 'BALON-FUT', 'price': 300, 'cost': 200, 'stock': 50, 'category': 'Deportes'},
        {'name': 'Raqueta de tenis', 'sku': 'RAQ-TEN', 'price': 1200, 'cost': 800, 'stock': 25, 'category': 'Deportes'},
        {'name': 'Libro Python', 'sku': 'LIB-PY', 'price': 400, 'cost': 300, 'stock': 60, 'category': 'Libros'}
    ]
    
    products = []
    for prod_data in products_data:
        category = next(cat for cat in categories if cat.name == prod_data['category'])
        product, created = Product.objects.get_or_create(
            sku=prod_data['sku'],
            defaults={
                'name': prod_data['name'],
                'price': Decimal(str(prod_data['price'])),
                'cost': Decimal(str(prod_data['cost'])),
                'stock': prod_data['stock'],
                'category': category,
                'description': f'Descripción de {prod_data["name"]}'
            }
        )
        products.append(product)
        print(f"Producto {product.name}: {'Creado' if created else 'Ya existe'}")
    
    # Crear clientes
    clients_data = [
        {'name': 'Juan Pérez', 'email': 'juan@email.com', 'phone': '555-0001'},
        {'name': 'María García', 'email': 'maria@email.com', 'phone': '555-0002'},
        {'name': 'Carlos López', 'email': 'carlos@email.com', 'phone': '555-0003'},
        {'name': 'Ana Martínez', 'email': 'ana@email.com', 'phone': '555-0004'},
        {'name': 'Luis Rodríguez', 'email': 'luis@email.com', 'phone': '555-0005'},
        {'name': 'Cliente Anónimo', 'email': 'anonimo@tienda.com', 'phone': '000-000-0000'}
    ]
    
    clients = []
    for client_data in clients_data:
        client, created = Client.objects.get_or_create(
            email=client_data['email'],
            defaults={
                'name': client_data['name'],
                'phone': client_data['phone']
            }
        )
        clients.append(client)
        print(f"Cliente {client.name}: {'Creado' if created else 'Ya existe'}")
    
    print("✅ Datos básicos creados exitosamente!")
    return products, clients

if __name__ == '__main__':
    create_basic_data()
