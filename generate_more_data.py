#!/usr/bin/env python
"""
Script para generar más datos de electrodomésticos
Permite agregar más productos, clientes y ventas sin limpiar la base de datos existente
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.db import transaction
from apps.core.models import User
from apps.products.models import Category, Product
from apps.clients.models import Client
from apps.sales.models import Sale, SaleItem
from django.utils import timezone

def generar_mas_productos(num_productos=50):
    """Generar más productos de electrodomésticos"""
    print(f"📦 Generando {num_productos} productos adicionales...")
    
    categorias = Category.objects.all()
    marcas = [
        'Samsung', 'LG', 'Sony', 'Panasonic', 'Toshiba', 'Hitachi', 'Daikin',
        'Mabe', 'Whirlpool', 'Maytag', 'GE', 'Frigidaire', 'KitchenAid',
        'Bosch', 'Electrolux', 'Haier', 'TCL', 'Hisense', 'Vizio',
        'Apple', 'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'MSI'
    ]
    
    tipos_productos = [
        'Refrigerador', 'Lavadora', 'Secadora', 'Estufa', 'Horno', 'Microondas',
        'Aire Acondicionado', 'Televisor', 'Smart TV', 'Laptop', 'Computadora',
        'Smartphone', 'Tablet', 'Bocina', 'Auriculares', 'Licuadora', 'Batidora',
        'Cafetera', 'Tostador', 'Plancha', 'Aspiradora', 'Impresora', 'Monitor'
    ]
    
    productos_creados = []
    sku_counter = Product.objects.count() + 1000
    
    for i in range(num_productos):
        categoria = random.choice(categorias)
        marca = random.choice(marcas)
        tipo = random.choice(tipos_productos)
        
        # Generar nombre del producto
        if 'TV' in tipo or 'Televisor' in tipo:
            pulgadas = random.choice(['32"', '43"', '50"', '55"', '65"', '75"'])
            tecnologia = random.choice(['LED', 'OLED', 'QLED', '4K', '8K'])
            nombre = f"Smart TV {marca} {pulgadas} {tecnologia}"
        elif 'Laptop' in tipo or 'Computadora' in tipo:
            modelo = random.choice(['Inspiron', 'Pavilion', 'IdeaPad', 'VivoBook', 'Aspire', 'ThinkPad'])
            nombre = f"{tipo} {marca} {modelo} {random.randint(10, 17)}\""
        elif 'Smartphone' in tipo:
            modelo = random.choice(['Galaxy', 'iPhone', 'P30', 'Mi', 'Redmi'])
            nombre = f"{marca} {modelo} {random.randint(10, 15)} {random.choice(['64GB', '128GB', '256GB'])}"
        else:
            capacidad = random.choice(['1.5L', '2L', '3L', '5L', '10L', '15L', '20L', '25L'])
            nombre = f"{tipo} {marca} {capacidad}"
        
        # Precio según tipo
        if 'TV' in tipo or 'Televisor' in tipo:
            precio_base = random.randint(3000, 50000)
        elif 'Laptop' in tipo or 'Computadora' in tipo:
            precio_base = random.randint(8000, 35000)
        elif 'Smartphone' in tipo:
            precio_base = random.randint(5000, 25000)
        elif 'Refrigerador' in tipo:
            precio_base = random.randint(8000, 25000)
        elif 'Lavadora' in tipo or 'Secadora' in tipo:
            precio_base = random.randint(5000, 15000)
        elif 'Aire' in tipo:
            precio_base = random.randint(3000, 12000)
        else:
            precio_base = random.randint(500, 5000)
        
        # Generar SKU único
        sku = f"ELEC-{sku_counter:06d}"
        sku_counter += 1
        
        # Calcular costo (70-85% del precio)
        costo = Decimal(str(precio_base * random.uniform(0.70, 0.85)))
        precio = Decimal(str(precio_base))
        
        # Stock aleatorio
        stock = random.randint(0, 50)
        min_stock = random.randint(5, 15)
        max_stock = random.randint(50, 100)
        
        # Peso y dimensiones
        peso = Decimal(str(random.uniform(1.0, 50.0)))
        dimensiones = f"{random.randint(30, 80)}x{random.randint(30, 60)}x{random.randint(30, 100)} cm"
        
        # Código de barras
        barcode = f"7{random.randint(100000000000, 999999999999)}"
        
        # Tags
        tags = f"{categoria.name}, {marca}, electrodoméstico, {tipo.lower()}"
        
        producto = Product.objects.create(
            name=nombre,
            description=f"Descripción detallada del {nombre}. Producto de alta calidad con garantía del fabricante. {marca} garantiza la mejor calidad y durabilidad.",
            sku=sku,
            price=precio,
            cost=costo,
            stock=stock,
            min_stock=min_stock,
            max_stock=max_stock,
            category=categoria,
            weight=peso,
            dimensions=dimensiones,
            barcode=barcode,
            tags=tags,
            is_digital=False
        )
        
        productos_creados.append(producto)
        print(f"  ✅ Producto: {producto.name} - ${producto.price}")
    
    return productos_creados

def generar_mas_clientes(num_clientes=50):
    """Generar más clientes"""
    print(f"👥 Generando {num_clientes} clientes adicionales...")
    
    nombres_base = [
        'Alejandro', 'Ana', 'Carlos', 'Carmen', 'David', 'Elena', 'Fernando', 'Gabriela',
        'Héctor', 'Isabel', 'Jorge', 'Laura', 'Manuel', 'Natalia', 'Oscar', 'Patricia',
        'Ricardo', 'Sandra', 'Tomás', 'Verónica', 'Ximena', 'Yolanda', 'Zacarías'
    ]
    
    apellidos_base = [
        'García', 'Rodríguez', 'Martínez', 'Hernández', 'López', 'González', 'Pérez',
        'Sánchez', 'Ramírez', 'Cruz', 'Flores', 'Gómez', 'Díaz', 'Reyes', 'Morales',
        'Jiménez', 'Álvarez', 'Ruiz', 'Torres', 'Vargas', 'Castillo', 'Romero',
        'Herrera', 'Medina', 'Aguilar', 'Mendoza', 'Guerrero', 'Rojas', 'Silva'
    ]
    
    ciudades = [
        'Ciudad de México', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana',
        'León', 'Juárez', 'Torreón', 'Querétaro', 'San Luis Potosí',
        'Mérida', 'Mexicali', 'Aguascalientes', 'Acapulco', 'Culiacán',
        'Saltillo', 'Hermosillo', 'Villahermosa', 'Chihuahua', 'Reynosa',
        'Tampico', 'Irapuato', 'Matamoros', 'Durango', 'Tuxtla Gutiérrez',
        'Ensenada', 'Xalapa', 'Mazatlán', 'Nuevo Laredo', 'Oaxaca',
        'Campeche', 'Chetumal', 'Colima', 'Toluca', 'Cuernavaca',
        'Tlaxcala', 'Pachuca', 'Chilpancingo', 'Zacatecas', 'La Paz'
    ]
    
    clientes_creados = []
    cliente_counter = Client.objects.count() + 1
    
    for i in range(num_clientes):
        nombre = random.choice(nombres_base)
        apellido1 = random.choice(apellidos_base)
        apellido2 = random.choice(apellidos_base)
        nombre_completo = f"{nombre} {apellido1} {apellido2}"
        
        email = f"cliente{cliente_counter}@email.com"
        cliente_counter += 1
        
        telefono = f"55{random.randint(10000000, 99999999)}"
        
        calles = ['Av. Reforma', 'Calle Juárez', 'Av. Insurgentes', 'Calle Hidalgo', 'Av. Chapultepec', 'Calle Morelos', 'Av. Universidad']
        numeros = random.randint(100, 9999)
        direccion = f"{random.choice(calles)} {numeros}, Col. Centro"
        
        ciudad = random.choice(ciudades)
        cp = f"{random.randint(10000, 99999)}"
        tipo_cliente = random.choice(['individual', 'business'])
        segmento = random.choice(['new', 'regular', 'vip'])
        
        fecha_nacimiento = datetime.now() - timedelta(days=random.randint(18*365, 80*365))
        
        cliente = Client.objects.create(
            name=nombre_completo,
            email=email,
            phone=telefono,
            address=direccion,
            city=ciudad,
            postal_code=cp,
            client_type=tipo_cliente,
            segment=segmento,
            birth_date=fecha_nacimiento.date(),
            notes=f"Cliente {tipo_cliente} de {ciudad} - Generado automáticamente",
            is_active=True
        )
        
        clientes_creados.append(cliente)
        print(f"  ✅ Cliente: {cliente.name} - {cliente.email}")
    
    return clientes_creados

def generar_mas_ventas(num_ventas=100):
    """Generar más ventas"""
    print(f"💰 Generando {num_ventas} ventas adicionales...")
    
    clientes = list(Client.objects.all())
    productos = list(Product.objects.all())
    usuarios = list(User.objects.filter(role__in=['seller', 'manager']))
    
    if not clientes or not productos or not usuarios:
        print("❌ No hay suficientes datos para generar ventas")
        return []
    
    fecha_inicio = datetime(2023, 1, 1)
    fecha_actual = datetime.now()
    
    ventas_creadas = []
    
    for i in range(num_ventas):
        # Fecha aleatoria entre 2023 y ahora
        dias_diferencia = (fecha_actual - fecha_inicio).days
        dias_aleatorios = random.randint(0, dias_diferencia)
        fecha_venta = fecha_inicio + timedelta(days=dias_aleatorios)
        
        # Cliente aleatorio
        cliente = random.choice(clientes)
        
        # Usuario aleatorio (vendedor)
        usuario = random.choice(usuarios)
        
        # Productos aleatorios (1-5 productos por venta)
        num_productos = random.randint(1, 5)
        productos_venta = random.sample(productos, num_productos)
        
        # Calcular totales
        subtotal = Decimal('0')
        items_venta = []
        
        for producto in productos_venta:
            cantidad = random.randint(1, 3)
            precio = producto.price
            subtotal_item = precio * cantidad
            subtotal += subtotal_item
            
            items_venta.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal_item
            })
        
        # Impuestos (16%)
        tax = subtotal * Decimal('0.16')
        
        # Descuento aleatorio (0-20%)
        descuento_porcentaje = random.randint(0, 20)
        descuento = subtotal * Decimal(str(descuento_porcentaje / 100))
        
        # Total final
        total = subtotal + tax - descuento
        
        # Estado de la venta
        estado = random.choice(['completed', 'pending', 'cancelled'])
        if estado == 'completed':
            payment_status = random.choice(['paid', 'partial'])
        else:
            payment_status = 'pending'
        
        # Crear venta con fecha específica
        fecha_venta_aware = timezone.make_aware(fecha_venta)
        venta = Sale.objects.create(
            client=cliente,
            user=usuario,
            subtotal=subtotal,
            tax=tax,
            discount=descuento,
            total=total,
            status=estado,
            payment_status=payment_status,
            notes=f"Venta generada automáticamente - {fecha_venta.strftime('%Y-%m-%d')}",
            transaction_id=f"TXN-{random.randint(100000, 999999)}"
        )
        
        # Actualizar fechas de creación y actualización
        venta.created_at = fecha_venta_aware
        venta.updated_at = fecha_venta_aware
        venta.save(update_fields=['created_at', 'updated_at'])
        
        # Crear items de la venta
        for item_data in items_venta:
            item = SaleItem.objects.create(
                sale=venta,
                product=item_data['producto'],
                quantity=item_data['cantidad'],
                price=item_data['precio']
            )
            # Actualizar fechas del item
            item.created_at = fecha_venta_aware
            item.updated_at = fecha_venta_aware
            item.save(update_fields=['created_at', 'updated_at'])
        
        # Actualizar estadísticas del cliente
        if estado == 'completed':
            cliente.total_purchases += total
            fecha_venta_aware = timezone.make_aware(fecha_venta)
            if not cliente.last_purchase_date or fecha_venta_aware > cliente.last_purchase_date:
                cliente.last_purchase_date = fecha_venta_aware
            cliente.save()
        
        ventas_creadas.append(venta)
        
        if i % 50 == 0:
            print(f"  ✅ Creadas {i+1} ventas...")
    
    print(f"  ✅ Total de ventas creadas: {len(ventas_creadas)}")
    return ventas_creadas

def main():
    """Función principal"""
    print("🚀 Generando más datos de electrodomésticos...")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # Generar más productos
            productos = generar_mas_productos(50)
            
            # Generar más clientes
            clientes = generar_mas_clientes(50)
            
            # Generar más ventas
            ventas = generar_mas_ventas(100)
        
        print("=" * 60)
        print("✅ Generación de datos completada exitosamente!")
        print(f"📊 Resumen:")
        print(f"  📦 Productos totales: {Product.objects.count()}")
        print(f"  👥 Clientes totales: {Client.objects.count()}")
        print(f"  💰 Ventas totales: {Sale.objects.count()}")
        print(f"  📋 Items de venta totales: {SaleItem.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error durante la generación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
