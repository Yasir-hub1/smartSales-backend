#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Seed para crear productos de electrodomésticos (máximo 50)
"""
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.products.models import Product, Category

# Lista de electrodomésticos
ELECTRODOMESTICOS = [
    {'name': 'Refrigerador Samsung 2 Puertas', 'sku': 'REF-SAM-001', 'price': 8999.00, 'cost': 6299.30, 'stock': 15, 'description': 'Refrigerador de 2 puertas, capacidad 350L'},
    {'name': 'Lavadora LG Carga Frontal 15kg', 'sku': 'LAV-LG-001', 'price': 7999.00, 'cost': 5599.30, 'stock': 12, 'description': 'Lavadora de carga frontal, 15kg de capacidad'},
    {'name': 'Microondas Panasonic 20L', 'sku': 'MIC-PAN-001', 'price': 1299.00, 'cost': 909.30, 'stock': 25, 'description': 'Microondas de 20 litros, panel digital'},
    {'name': 'Licuadora Oster Pro', 'sku': 'LIC-OST-001', 'price': 899.00, 'cost': 629.30, 'stock': 30, 'description': 'Licuadora profesional, 3 velocidades'},
    {'name': 'Batidora KitchenAid', 'sku': 'BAT-KIT-001', 'price': 2499.00, 'cost': 1749.30, 'stock': 8, 'description': 'Batidora de pie, 5 velocidades'},
    {'name': 'Tostador Black+Decker', 'sku': 'TOS-BLA-001', 'price': 599.00, 'cost': 419.30, 'stock': 20, 'description': 'Tostador de 2 ranuras, extracción automática'},
    {'name': 'Cafetera Nespresso', 'sku': 'CAF-NES-001', 'price': 1999.00, 'cost': 1399.30, 'stock': 15, 'description': 'Cafetera de cápsulas, sistema espresso'},
    {'name': 'Aspiradora Dyson V15', 'sku': 'ASP-DYS-001', 'price': 8999.00, 'cost': 6299.30, 'stock': 5, 'description': 'Aspiradora inalámbrica, tecnología láser'},
    {'name': 'Plancha a Vapor Rowenta', 'sku': 'PLA-ROW-001', 'price': 1299.00, 'cost': 909.30, 'stock': 18, 'description': 'Plancha de vapor, sistema anti-cal'},
    {'name': 'Ventilador de Torre Bionaire', 'sku': 'VEN-BIO-001', 'price': 1499.00, 'cost': 1049.30, 'stock': 22, 'description': 'Ventilador de torre, control remoto'},
    {'name': 'Aire Acondicionado Midea 1.5 Ton', 'sku': 'AIR-MID-001', 'price': 8999.00, 'cost': 6299.30, 'stock': 10, 'description': 'Aire acondicionado split, inverter'},
    {'name': 'Horno Eléctrico Whirlpool', 'sku': 'HOR-WHI-001', 'price': 5999.00, 'cost': 4199.30, 'stock': 7, 'description': 'Horno eléctrico empotrable, 70L'},
    {'name': 'Estufa de Inducción Bosch', 'sku': 'EST-BOS-001', 'price': 6999.00, 'cost': 4899.30, 'stock': 9, 'description': 'Estufa de inducción, 4 quemadores'},
    {'name': 'Lavavajillas Mabe', 'sku': 'LAV-MAB-001', 'price': 7999.00, 'cost': 5599.30, 'stock': 11, 'description': 'Lavavajillas empotrable, 14 cubiertos'},
    {'name': 'Secadora de Ropa GE', 'sku': 'SEC-GE-001', 'price': 8999.00, 'cost': 6299.30, 'stock': 6, 'description': 'Secadora de ropa, carga frontal, 20kg'},
    {'name': 'Purificador de Aire Xiaomi', 'sku': 'PUR-XIA-001', 'price': 2499.00, 'cost': 1749.30, 'stock': 14, 'description': 'Purificador de aire, filtro HEPA'},
    {'name': 'Vaporizador Humidificador', 'sku': 'VAP-HUM-001', 'price': 799.00, 'cost': 559.30, 'stock': 19, 'description': 'Vaporizador humidificador, 2L'},
    {'name': 'Cocina Eléctrica Frigidaire', 'sku': 'COC-FRI-001', 'price': 6999.00, 'cost': 4899.30, 'stock': 8, 'description': 'Cocina eléctrica, 4 quemadores'},
    {'name': 'Freidora de Aire Ninja', 'sku': 'FRE-NIN-001', 'price': 2999.00, 'cost': 2099.30, 'stock': 16, 'description': 'Freidora de aire, capacidad 5.5L'},
    {'name': 'Olla Arrocera Cuckoo', 'sku': 'OLL-CUC-001', 'price': 1299.00, 'cost': 909.30, 'stock': 21, 'description': 'Olla arrocera, capacidad 10 tazas'},
    {'name': 'Procesador de Alimentos Cuisinart', 'sku': 'PRO-CUI-001', 'price': 3499.00, 'cost': 2449.30, 'stock': 13, 'description': 'Procesador de alimentos, 14 tazas'},
    {'name': 'Exprimidor de Naranjas Breville', 'sku': 'EXP-BRE-001', 'price': 1999.00, 'cost': 1399.30, 'stock': 17, 'description': 'Exprimidor de naranjas, eléctrico'},
    {'name': 'Sandwichera Hamilton Beach', 'sku': 'SAN-HAM-001', 'price': 899.00, 'cost': 629.30, 'stock': 24, 'description': 'Sandwichera, placas antiadherentes'},
    {'name': 'Waflera Oster', 'sku': 'WAF-OST-001', 'price': 1299.00, 'cost': 909.30, 'stock': 19, 'description': 'Waflera, placas reversibles'},
    {'name': 'Molino de Café Baratza', 'sku': 'MOL-BAR-001', 'price': 2999.00, 'cost': 2099.30, 'stock': 11, 'description': 'Molino de café, muelas cónicas'},
    {'name': 'Hervidor Eléctrico Breville', 'sku': 'HER-BRE-001', 'price': 1499.00, 'cost': 1049.30, 'stock': 23, 'description': 'Hervidor eléctrico, 1.7L'},
    {'name': 'Plancha de Pelo Dyson', 'sku': 'PLA-DYS-001', 'price': 3999.00, 'cost': 2799.30, 'stock': 9, 'description': 'Plancha de pelo, tecnología aire'},
    {'name': 'Secador de Pelo Remington', 'sku': 'SEC-REM-001', 'price': 1299.00, 'cost': 909.30, 'stock': 18, 'description': 'Secador de pelo, 1875W'},
    {'name': 'Afeitadora Eléctrica Philips', 'sku': 'AFE-PHI-001', 'price': 1999.00, 'cost': 1399.30, 'stock': 20, 'description': 'Afeitadora eléctrica, recargable'},
    {'name': 'Cepillo Dental Eléctrico Oral-B', 'sku': 'CEP-ORA-001', 'price': 899.00, 'cost': 629.30, 'stock': 27, 'description': 'Cepillo dental eléctrico, recargable'},
    {'name': 'Robot Aspirador iRobot', 'sku': 'ROB-IRO-001', 'price': 9999.00, 'cost': 6999.30, 'stock': 4, 'description': 'Robot aspirador, programable'},
    {'name': 'Lámpara Inteligente Philips Hue', 'sku': 'LAM-PHI-001', 'price': 799.00, 'cost': 559.30, 'stock': 28, 'description': 'Lámpara inteligente, RGB, WiFi'},
    {'name': 'Enfriador de Aire Evaporativo', 'sku': 'ENF-EVA-001', 'price': 2999.00, 'cost': 2099.30, 'stock': 12, 'description': 'Enfriador evaporativo, 40L'},
    {'name': 'Deshumidificador Frigidaire', 'sku': 'DES-FRI-001', 'price': 3999.00, 'cost': 2799.30, 'stock': 8, 'description': 'Deshumidificador, 50 pintas'},
    {'name': 'Calentador de Agua Rheem', 'sku': 'CAL-RHE-001', 'price': 5999.00, 'cost': 4199.30, 'stock': 6, 'description': 'Calentador de agua, 40 galones'},
    {'name': 'Dispensador de Agua Brio', 'sku': 'DIS-BRI-001', 'price': 2999.00, 'cost': 2099.30, 'stock': 14, 'description': 'Dispensador de agua, frío y caliente'},
    {'name': 'Cocina de Inducción Portátil', 'sku': 'COC-POR-001', 'price': 1499.00, 'cost': 1049.30, 'stock': 17, 'description': 'Cocina de inducción, portátil'},
    {'name': 'Olla de Presión Eléctrica Instant Pot', 'sku': 'OLL-INS-001', 'price': 2999.00, 'cost': 2099.30, 'stock': 15, 'description': 'Olla de presión eléctrica, 6L'},
    {'name': 'Máquina de Yogur Yonanas', 'sku': 'MAQ-YON-001', 'price': 1999.00, 'cost': 1399.30, 'stock': 10, 'description': 'Máquina para hacer yogur'},
    {'name': 'Deshidratador de Alimentos Excalibur', 'sku': 'DES-EXC-001', 'price': 4999.00, 'cost': 3499.30, 'stock': 7, 'description': 'Deshidratador de alimentos, 9 bandejas'},
]

def seed_products():
    """Crear productos de electrodomésticos"""
    # Crear o obtener categoría de electrodomésticos
    category, created = Category.objects.get_or_create(
        name='Electrodomésticos',
        defaults={'description': 'Electrodomésticos para el hogar'}
    )
    
    if created:
        print(f'Categoría "{category.name}" creada')
    else:
        print(f'Usando categoría existente: "{category.name}')
    
    # Limitar a 50 productos
    productos_a_crear = ELECTRODOMESTICOS[:50]
    
    created_count = 0
    updated_count = 0
    
    for producto_data in productos_a_crear:
        sku = producto_data['sku']
        
        # Verificar si ya existe
        producto, created = Product.objects.get_or_create(
            sku=sku,
            defaults={
                'name': producto_data['name'],
                'description': producto_data.get('description', ''),
                'price': producto_data['price'],
                'cost': producto_data.get('cost', producto_data['price'] * 0.7),
                'stock': producto_data.get('stock', random.randint(5, 50)),
                'min_stock': 10,
                'max_stock': 1000,
                'category': category,
                'barcode': f'{random.randint(1000000000000, 9999999999999)}',
                'tags': 'electrodoméstico, hogar',
                'is_digital': False,
            }
        )
        
        if created:
            created_count += 1
            print(f'✓ Producto creado: {producto.name} ({sku})')
        else:
            # Actualizar stock si existe
            producto.stock = producto_data.get('stock', random.randint(5, 50))
            producto.save()
            updated_count += 1
            print(f'↻ Producto actualizado: {producto.name} ({sku})')
    
    print(f'\n=== Resumen ===')
    print(f'Productos creados: {created_count}')
    print(f'Productos actualizados: {updated_count}')
    print(f'Total procesados: {created_count + updated_count}')

if __name__ == '__main__':
    print('=== Creando productos de electrodomésticos ===\n')
    seed_products()
    print('\n✓ Proceso completado')

