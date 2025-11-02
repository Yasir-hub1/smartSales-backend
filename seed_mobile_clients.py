#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Seed para crear clientes (máximo 10)
"""
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.clients.models import Client
from django.utils import timezone

# Lista de clientes
CLIENTES = [
    {'name': 'Juan Pérez García', 'email': 'juan.perez@email.com', 'phone': '5551234567', 'city': 'Ciudad de México', 'client_type': 'individual', 'segment': 'vip'},
    {'name': 'María González López', 'email': 'maria.gonzalez@email.com', 'phone': '5552345678', 'city': 'Guadalajara', 'client_type': 'individual', 'segment': 'regular'},
    {'name': 'Carlos Rodríguez Martínez', 'email': 'carlos.rodriguez@email.com', 'phone': '5553456789', 'city': 'Monterrey', 'client_type': 'individual', 'segment': 'vip'},
    {'name': 'Ana Martínez Sánchez', 'email': 'ana.martinez@email.com', 'phone': '5554567890', 'city': 'Puebla', 'client_type': 'individual', 'segment': 'regular'},
    {'name': 'Roberto Hernández Díaz', 'email': 'roberto.hernandez@email.com', 'phone': '5555678901', 'city': 'Tijuana', 'client_type': 'individual', 'segment': 'new'},
    {'name': 'Laura Fernández Ramírez', 'email': 'laura.fernandez@email.com', 'phone': '5556789012', 'city': 'León', 'client_type': 'individual', 'segment': 'regular'},
    {'name': 'ElectroMéxico S.A. de C.V.', 'email': 'contacto@electromexico.com', 'phone': '5557890123', 'city': 'Ciudad de México', 'client_type': 'business', 'segment': 'vip'},
    {'name': 'Hogar Plus Distribuidora', 'email': 'ventas@hogarplus.com', 'phone': '5558901234', 'city': 'Guadalajara', 'client_type': 'business', 'segment': 'regular'},
    {'name': 'Tecnología del Hogar S.A.', 'email': 'info@tecnohogar.com', 'phone': '5559012345', 'city': 'Monterrey', 'client_type': 'business', 'segment': 'vip'},
    {'name': 'Patricia Morales Vázquez', 'email': 'patricia.morales@email.com', 'phone': '5550123456', 'city': 'Cancún', 'client_type': 'individual', 'segment': 'new'},
]

def seed_clients():
    """Crear clientes"""
    # Limitar a 10 clientes
    clientes_a_crear = CLIENTES[:10]
    
    created_count = 0
    updated_count = 0
    
    for cliente_data in clientes_a_crear:
        email = cliente_data['email']
        
        # Generar fecha de última compra aleatoria (últimos 30 días)
        last_purchase_days = random.randint(0, 30)
        last_purchase_date = timezone.now() - timedelta(days=last_purchase_days)
        
        # Generar total de compras aleatorio
        total_purchases = random.uniform(1000.00, 50000.00)
        
        # Verificar si ya existe
        cliente, created = Client.objects.get_or_create(
            email=email,
            defaults={
                'name': cliente_data['name'],
                'phone': cliente_data.get('phone', ''),
                'city': cliente_data.get('city', ''),
                'country': 'México',
                'client_type': cliente_data.get('client_type', 'individual'),
                'segment': cliente_data.get('segment', 'new'),
                'last_purchase_date': last_purchase_date,
                'total_purchases': total_purchases,
                'is_active': True,
            }
        )
        
        if created:
            created_count += 1
            print(f'✓ Cliente creado: {cliente.name} ({email})')
        else:
            # Actualizar datos si existe
            cliente.name = cliente_data['name']
            cliente.phone = cliente_data.get('phone', '')
            cliente.city = cliente_data.get('city', '')
            cliente.client_type = cliente_data.get('client_type', 'individual')
            cliente.segment = cliente_data.get('segment', 'new')
            cliente.last_purchase_date = last_purchase_date
            cliente.total_purchases = total_purchases
            cliente.save()
            updated_count += 1
            print(f'↻ Cliente actualizado: {cliente.name} ({email})')
    
    print(f'\n=== Resumen ===')
    print(f'Clientes creados: {created_count}')
    print(f'Clientes actualizados: {updated_count}')
    print(f'Total procesados: {created_count + updated_count}')

if __name__ == '__main__':
    print('=== Creando clientes ===\n')
    seed_clients()
    print('\n✓ Proceso completado')

