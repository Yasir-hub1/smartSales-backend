#!/usr/bin/env python
"""
Script para verificar que las ventas se pueden consultar correctamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.sales.models import Sale, SaleItem
from django.db.models import Count, Sum
from django.utils import timezone

def verificar_ventas_detalladas():
    """Verificar las ventas con detalles completos"""
    print("🔍 Verificando ventas en detalle...")
    print("=" * 60)
    
    # Obtener todas las ventas ordenadas por fecha
    ventas = Sale.objects.all().order_by('created_at')
    
    print(f"📊 Total de ventas: {ventas.count()}")
    
    # Mostrar las primeras 5 ventas con detalles
    print("\n📅 Primeras 5 ventas con detalles:")
    print("-" * 80)
    for i, venta in enumerate(ventas[:5], 1):
        print(f"{i}. Venta ID: {venta.id}")
        print(f"   Cliente: {venta.client.name}")
        print(f"   Vendedor: {venta.user.get_full_name()}")
        print(f"   Fecha: {venta.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Estado: {venta.get_status_display()}")
        print(f"   Pago: {venta.get_payment_status_display()}")
        print(f"   Total: ${venta.total:,.2f}")
        print(f"   Items: {venta.items.count()}")
        
        # Mostrar items de la venta
        for item in venta.items.all():
            print(f"     - {item.product.name} x {item.quantity} = ${item.subtotal:,.2f}")
        print()
    
    # Mostrar las últimas 5 ventas
    print("📅 Últimas 5 ventas:")
    print("-" * 80)
    ultimas_ventas = Sale.objects.all().order_by('-created_at')[:5]
    for i, venta in enumerate(ultimas_ventas, 1):
        print(f"{i}. {venta.created_at.strftime('%Y-%m-%d %H:%M')} - {venta.client.name} - ${venta.total:,.2f}")
    
    # Estadísticas por año
    print("\n📊 Estadísticas por año:")
    print("-" * 40)
    
    ventas_por_ano = Sale.objects.extra(
        select={'year': 'strftime("%%Y", created_at)'}
    ).values('year').annotate(
        total_ventas=Count('id'),
        total_monto=Sum('total')
    ).order_by('year')
    
    for venta_ano in ventas_por_ano:
        ventas_completadas = Sale.objects.filter(created_at__year=venta_ano['year'], status='completed').count()
        print(f"Año {venta_ano['year']}:")
        print(f"  Ventas: {venta_ano['total_ventas']}")
        print(f"  Completadas: {ventas_completadas}")
        print(f"  Total: ${venta_ano['total_monto']:,.2f}")
        print()
    
    # Verificar que las fechas están correctas
    print("🔍 Verificación de fechas:")
    print("-" * 40)
    
    venta_antigua = Sale.objects.order_by('created_at').first()
    venta_reciente = Sale.objects.order_by('-created_at').first()
    
    if venta_antigua:
        print(f"Venta más antigua: {venta_antigua.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Cliente: {venta_antigua.client.name}")
        print(f"  Total: ${venta_antigua.total:,.2f}")
    
    if venta_reciente:
        print(f"Venta más reciente: {venta_reciente.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Cliente: {venta_reciente.client.name}")
        print(f"  Total: ${venta_reciente.total:,.2f}")
    
    # Verificar que las fechas están en el rango correcto
    ventas_2023 = Sale.objects.filter(created_at__year=2023).count()
    ventas_2024 = Sale.objects.filter(created_at__year=2024).count()
    ventas_2025 = Sale.objects.filter(created_at__year=2025).count()
    
    print(f"\n📅 Distribución por año:")
    print(f"  2023: {ventas_2023} ventas")
    print(f"  2024: {ventas_2024} ventas")
    print(f"  2025: {ventas_2025} ventas")
    
    # Verificar que no hay ventas futuras
    ventas_futuras = Sale.objects.filter(created_at__gt=timezone.now()).count()
    print(f"\n🚫 Ventas futuras: {ventas_futuras}")
    
    if ventas_futuras == 0:
        print("✅ Todas las ventas están en el pasado")
    else:
        print("⚠️ Hay ventas con fechas futuras")

def verificar_items_venta():
    """Verificar los items de venta"""
    print("\n📋 Verificando items de venta...")
    print("=" * 60)
    
    total_items = SaleItem.objects.count()
    print(f"Total de items de venta: {total_items}")
    
    # Items por venta
    items_por_venta = SaleItem.objects.values('sale__id').annotate(
        total_items=Count('id')
    ).order_by('-total_items')
    
    print("\nTop 5 ventas con más items:")
    for item in items_por_venta[:5]:
        venta = Sale.objects.get(id=item['sale__id'])
        print(f"  Venta {venta.id}: {item['total_items']} items - ${venta.total:,.2f}")
    
    # Productos más vendidos
    productos_mas_vendidos = SaleItem.objects.values('product__name').annotate(
        total_vendido=Sum('quantity')
    ).order_by('-total_vendido')[:5]
    
    print("\nTop 5 productos más vendidos:")
    for producto in productos_mas_vendidos:
        print(f"  {producto['product__name']}: {producto['total_vendido']} unidades")

def main():
    """Función principal"""
    print("🔍 Verificando ventas en la base de datos...")
    print("=" * 60)
    
    try:
        verificar_ventas_detalladas()
        verificar_items_venta()
        
        print("\n" + "=" * 60)
        print("✅ Verificación completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
