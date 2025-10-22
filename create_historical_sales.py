#!/usr/bin/env python
"""
Script para crear ventas históricas con fechas específicas desde 2023
Distribuye las ventas de manera más realista a lo largo del tiempo
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

def crear_ventas_historicas():
    """Crear ventas históricas con fechas específicas desde 2023"""
    print("📅 Creando ventas históricas desde 2023...")
    
    clientes = list(Client.objects.all())
    productos = list(Product.objects.all())
    usuarios = list(User.objects.filter(role__in=['seller', 'manager']))
    
    if not clientes or not productos or not usuarios:
        print("❌ No hay suficientes datos para generar ventas")
        return []
    
    # Períodos específicos con diferentes volúmenes de ventas
    periodos_ventas = [
        # 2023 - Año completo
        {
            'inicio': datetime(2023, 1, 1),
            'fin': datetime(2023, 12, 31),
            'ventas_por_mes': 15,  # 15 ventas por mes en 2023
            'descripcion': '2023 - Año de lanzamiento'
        },
        # 2024 - Crecimiento
        {
            'inicio': datetime(2024, 1, 1),
            'fin': datetime(2024, 12, 31),
            'ventas_por_mes': 25,  # 25 ventas por mes en 2024
            'descripcion': '2024 - Año de crecimiento'
        },
        # 2025 - Consolidación (hasta octubre)
        {
            'inicio': datetime(2025, 1, 1),
            'fin': datetime(2025, 10, 31),
            'ventas_por_mes': 30,  # 30 ventas por mes en 2025
            'descripcion': '2025 - Año de consolidación'
        }
    ]
    
    ventas_creadas = []
    
    for periodo in periodos_ventas:
        print(f"\n📊 {periodo['descripcion']}")
        print(f"   📅 Período: {periodo['inicio'].strftime('%Y-%m-%d')} a {periodo['fin'].strftime('%Y-%m-%d')}")
        print(f"   🎯 Ventas por mes: {periodo['ventas_por_mes']}")
        
        # Calcular meses en el período
        meses_periodo = []
        fecha_actual = periodo['inicio']
        while fecha_actual <= periodo['fin']:
            # Primer día del mes
            primer_dia = fecha_actual.replace(day=1)
            # Último día del mes
            if fecha_actual.month == 12:
                ultimo_dia = fecha_actual.replace(year=fecha_actual.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                ultimo_dia = fecha_actual.replace(month=fecha_actual.month + 1, day=1) - timedelta(days=1)
            
            meses_periodo.append({
                'inicio': primer_dia,
                'fin': ultimo_dia,
                'nombre': fecha_actual.strftime('%B %Y')
            })
            
            # Siguiente mes
            if fecha_actual.month == 12:
                fecha_actual = fecha_actual.replace(year=fecha_actual.year + 1, month=1)
            else:
                fecha_actual = fecha_actual.replace(month=fecha_actual.month + 1)
        
        # Crear ventas para cada mes
        for mes in meses_periodo:
            print(f"   📅 {mes['nombre']}: {periodo['ventas_por_mes']} ventas")
            
            for i in range(periodo['ventas_por_mes']):
                # Fecha aleatoria dentro del mes
                dias_mes = (mes['fin'] - mes['inicio']).days
                dias_aleatorios = random.randint(0, dias_mes)
                fecha_venta = mes['inicio'] + timedelta(days=dias_aleatorios)
                
                # Hora aleatoria del día
                hora = random.randint(9, 18)  # Horario comercial
                minuto = random.randint(0, 59)
                fecha_venta = fecha_venta.replace(hour=hora, minute=minuto)
                
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
                
                # Estado de la venta (más realista según el tiempo)
                if fecha_venta < datetime.now() - timedelta(days=30):
                    # Ventas antiguas más probable que estén completadas
                    estado = random.choices(
                        ['completed', 'pending', 'cancelled'],
                        weights=[80, 15, 5]
                    )[0]
                else:
                    # Ventas recientes más variadas
                    estado = random.choices(
                        ['completed', 'pending', 'cancelled'],
                        weights=[60, 30, 10]
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
                    notes=f"Venta histórica - {fecha_venta.strftime('%Y-%m-%d %H:%M')}",
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
                    if not cliente.last_purchase_date or fecha_venta_aware > cliente.last_purchase_date:
                        cliente.last_purchase_date = fecha_venta_aware
                    cliente.save()
                
                ventas_creadas.append(venta)
    
    print(f"\n✅ Total de ventas históricas creadas: {len(ventas_creadas)}")
    return ventas_creadas

def mostrar_estadisticas_historicas():
    """Mostrar estadísticas de las ventas históricas"""
    print("\n📊 Estadísticas de Ventas Históricas:")
    print("=" * 50)
    
    from django.db.models import Count, Sum
    from django.db.models.functions import TruncMonth
    
    # Ventas por año
    ventas_por_ano = Sale.objects.extra(
        select={'year': 'strftime("%%Y", created_at)'}
    ).values('year').annotate(
        total_ventas=Count('id'),
        total_monto=Sum('total')
    ).order_by('year')
    
    print("📅 Ventas por Año:")
    for venta_ano in ventas_por_ano:
        print(f"  {venta_ano['year']}: {venta_ano['total_ventas']} ventas - ${venta_ano['total_monto']:,.2f}")
    
    # Ventas por mes (últimos 12 meses)
    from datetime import datetime, timedelta
    fecha_limite = datetime.now() - timedelta(days=365)
    
    ventas_por_mes = Sale.objects.filter(
        created_at__gte=timezone.make_aware(fecha_limite)
    ).extra(
        select={'month': 'strftime("%%Y-%%m", created_at)'}
    ).values('month').annotate(
        total_ventas=Count('id'),
        total_monto=Sum('total')
    ).order_by('month')
    
    print("\n📅 Ventas por Mes (últimos 12 meses):")
    for venta_mes in ventas_por_mes:
        print(f"  {venta_mes['month']}: {venta_mes['total_ventas']} ventas - ${venta_mes['total_monto']:,.2f}")
    
    # Productos más vendidos
    from django.db.models import Sum
    productos_mas_vendidos = SaleItem.objects.values('product__name').annotate(
        total_vendido=Sum('quantity')
    ).order_by('-total_vendido')[:10]
    
    print("\n🏆 Top 10 Productos Más Vendidos:")
    for i, item in enumerate(productos_mas_vendidos, 1):
        print(f"  {i:2d}. {item['product__name']} - {item['total_vendido']} unidades")

def main():
    """Función principal"""
    print("🚀 Creando ventas históricas desde 2023...")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # Crear ventas históricas
            ventas = crear_ventas_historicas()
            
            # Mostrar estadísticas
            mostrar_estadisticas_historicas()
            
        print("\n" + "=" * 60)
        print("✅ Ventas históricas creadas exitosamente!")
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
