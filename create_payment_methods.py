#!/usr/bin/env python
"""
Script para agregar métodos de pago a la base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.payments.models import PaymentMethod

def create_payment_methods():
    """Crear métodos de pago por defecto"""
    print("Creando métodos de pago...")
    
    # Métodos de pago por defecto
    default_methods = [
        {
            'name': 'Tarjeta de Crédito/Débito',
            'code': 'stripe',
            'is_active': True,
            'is_online': True,
            'icon': 'credit-card',
            'description': 'Pago seguro con tarjeta de crédito o débito',
            'sort_order': 1
        },
        {
            'name': 'Efectivo',
            'code': 'cash',
            'is_active': True,
            'is_online': False,
            'icon': 'money-bill',
            'description': 'Pago en efectivo al recibir el producto',
            'sort_order': 2
        },
        {
            'name': 'Transferencia Bancaria',
            'code': 'transfer',
            'is_active': True,
            'is_online': False,
            'icon': 'university',
            'description': 'Transferencia bancaria directa',
            'sort_order': 3
        }
    ]
    
    for method_data in default_methods:
        method, created = PaymentMethod.objects.get_or_create(
            code=method_data['code'],
            defaults=method_data
        )
        if created:
            print(f'✓ Creado: {method.name}')
        else:
            print(f'→ Ya existe: {method.name}')
    
    print(f"\nTotal de métodos de pago: {PaymentMethod.objects.count()}")

if __name__ == '__main__':
    create_payment_methods()
