#!/usr/bin/env python
"""
Script para crear exactamente 50 ventas históricas desde 2023 hasta 2025
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
from django.utils import timezone
from django.db.models import Sum
from apps.core.models import User
from apps.products.models import Product
from apps.clients.models import Client
from apps.sales.models import Sale, SaleItem

def limpiar_ventas_existentes():
    """Limpiar todas las ventas existentes"""
    print("🧹 Limpiando ventas existentes...")
    
    # Eliminar items de venta primero
    SaleItem.objects.all().delete()
    
    # Eliminar ventas
    Sale.objects.all().delete()
    
    print("✅ Ventas limpiadas exitosamente")

def crear_50_ventas_historicas():
    """Crear exactamente 50 ventas distribuidas desde 2023 hasta 2025"""
    print("📅 Creando 50 ventas históricas desde 2023 hasta 2025...")
    
    clientes = list(Client.objects.all())
    productos = list(Product.objects.all())
    usuarios = list(User.objects.filter(role__in=['seller', 'manager']))
    
    if not clientes or not productos or not usuarios:
        print("❌ No hay suficientes datos para generar ventas")
        return []
    
    # Distribución de 50 ventas desde 2023 hasta 2025
    distribucion_ventas = [
        # 2023 - 15 ventas
        {'año': 2023, 'meses': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'ventas_por_mes': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]},
        # 2024 - 20 ventas  
        {'año': 2024, 'meses': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'ventas_por_mes': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]},
        # 2025 - 15 ventas (hasta octubre)
        {'año': 2025, 'meses': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 'ventas_por_mes': [2, 2, 2, 2, 2, 2, 2, 2, 2, 1]}
    ]
    
    ventas_creadas = []
    contador_ventas = 0
    
    for periodo in distribucion_ventas:
        año = periodo['año']
        meses = periodo['meses']
        ventas_por_mes = periodo['ventas_por_mes']
        
        print(f"\n📊 Año {año}: {sum(ventas_por_mes)} ventas")
        
        for i, mes in enumerate(meses):
            num_ventas_mes = ventas_por_mes[i] if i < len(ventas_por_mes) else 0
            
            if num_ventas_mes == 0:
                continue
                
            print(f"  📅 {mes:02d}/{año}: {num_ventas_mes} ventas")
            
            for j in range(num_ventas_mes):
                # Fecha aleatoria dentro del mes
                primer_dia = datetime(año, mes, 1)
                if mes == 12:
                    ultimo_dia = datetime(año + 1, 1, 1) - timedelta(days=1)
                else:
                    ultimo_dia = datetime(año, mes + 1, 1) - timedelta(days=1)
                
                dias_mes = (ultimo_dia - primer_dia).days
                dias_aleatorios = random.randint(0, dias_mes)
                fecha_venta = primer_dia + timedelta(days=dias_aleatorios)
                
                # Hora aleatoria del día (horario comercial)
                hora = random.randint(9, 18)
                minuto = random.randint(0, 59)
                fecha_venta = fecha_venta.replace(hour=hora, minute=minuto)
                
                # Cliente aleatorio
                cliente = random.choice(clientes)
                
                # Usuario aleatorio (vendedor)
                usuario = random.choice(usuarios)
                
                # Productos aleatorios (1-3 productos por venta)
                num_productos = random.randint(1, 3)
                productos_venta = random.sample(productos, num_productos)
                
                # Calcular totales
                subtotal = Decimal('0')
                items_venta = []
                
                for producto in productos_venta:
                    cantidad = random.randint(1, 2)
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
                
                # Descuento aleatorio (0-15%)
                descuento_porcentaje = random.randint(0, 15)
                descuento = subtotal * Decimal(str(descuento_porcentaje / 100))
                
                # Total final
                total = subtotal + tax - descuento
                
                # Estado de la venta (más realista según el tiempo)
                if fecha_venta < datetime.now() - timedelta(days=30):
                    # Ventas antiguas más probable que estén completadas
                    estado = random.choices(
                        ['completed', 'pending', 'cancelled'],
                        weights=[85, 10, 5]
                    )[0]
                else:
                    # Ventas recientes más variadas
                    estado = random.choices(
                        ['completed', 'pending', 'cancelled'],
                        weights=[70, 25, 5]
                    )[0]
                
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
                    notes=f"Venta histórica {contador_ventas + 1} - {fecha_venta.strftime('%Y-%m-%d %H:%M')}",
                    transaction_id=f"TXN-{contador_ventas + 1:06d}"
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
                    if not cliente.last_purchase_date or fecha_venta_aware > cliente.last_purchase_date:
                        cliente.last_purchase_date = fecha_venta_aware
                    cliente.save()
                
                ventas_creadas.append(venta)
                contador_ventas += 1
                
                print(f"    ✅ Venta {contador_ventas}: {fecha_venta.strftime('%Y-%m-%d %H:%M')} - ${total:,.2f}")
    
    print(f"\n✅ Total de ventas creadas: {len(ventas_creadas)}")
    return ventas_creadas

def mostrar_estadisticas():
    """Mostrar estadísticas de las ventas creadas"""
    print("\n📊 Estadísticas de Ventas Históricas:")
    print("=" * 60)
    
    from django.db.models import Count
    
    # Fecha más antigua y más reciente
    venta_antigua = Sale.objects.order_by('created_at').first()
    venta_reciente = Sale.objects.order_by('-created_at').first()
    
    if venta_antigua and venta_reciente:
        print(f"📅 Venta más antigua: {venta_antigua.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 Venta más reciente: {venta_reciente.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ventas por año
    ventas_por_ano = Sale.objects.extra(
        select={'year': 'strftime("%%Y", created_at)'}
    ).values('year').annotate(
        total=Count('id')
    ).order_by('year')
    
    print("\n📅 Ventas por año:")
    for venta_ano in ventas_por_ano:
        print(f"  {venta_ano['year']}: {venta_ano['total']} ventas")
    
    # Ventas por mes
    ventas_por_mes = Sale.objects.extra(
        select={'month': 'strftime("%%Y-%%m", created_at)'}
    ).values('month').annotate(
        total=Count('id')
    ).order_by('month')
    
    print("\n📅 Ventas por mes:")
    for venta_mes in ventas_por_mes:
        print(f"  {venta_mes['month']}: {venta_mes['total']} ventas")
    
    # Total de ingresos
    total_ingresos = Sale.objects.aggregate(Sum('total'))['total__sum'] or 0
    print(f"\n💰 Total de ingresos: ${total_ingresos:,.2f}")
    
    # Ventas completadas
    ventas_completadas = Sale.objects.filter(status='completed').count()
    total_ventas = Sale.objects.count()
    print(f"✅ Ventas completadas: {ventas_completadas}/{total_ventas} ({ventas_completadas/total_ventas*100:.1f}%)")

def main():
    """Función principal"""
    print("🚀 Creando 50 ventas históricas desde 2023 hasta 2025...")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # Limpiar ventas existentes
            limpiar_ventas_existentes()
            
            # Crear 50 ventas históricas
            ventas = crear_50_ventas_historicas()
            
            # Mostrar estadísticas
            mostrar_estadisticas()
            
        print("\n" + "=" * 60)
        print("✅ 50 ventas históricas creadas exitosamente!")
        print(f"📊 Resumen:")
        print(f"  💰 Total de ventas: {Sale.objects.count()}")
        print(f"  📋 Items de venta: {SaleItem.objects.count()}")
        print(f"  💵 Total de ingresos: ${Sale.objects.aggregate(Sum('total'))['total__sum']:,.2f}")
        
    except Exception as e:
        print(f"❌ Error durante la creación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
