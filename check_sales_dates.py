#!/usr/bin/env python
"""
Script para verificar las fechas de las ventas creadas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.sales.models import Sale
from django.db.models import Count
from django.utils import timezone

def verificar_fechas_ventas():
    """Verificar las fechas de las ventas"""
    print("📅 Verificando fechas de ventas...")
    print("=" * 60)
    
    # Obtener algunas ventas para verificar fechas
    ventas = Sale.objects.all().order_by('created_at')[:10]
    
    print('📅 Primeras 10 ventas con sus fechas:')
    print('=' * 60)
    for venta in ventas:
        fecha_creacion = venta.created_at.strftime('%Y-%m-%d %H:%M:%S')
        print(f'Venta {venta.id} - Cliente: {venta.client.name} - Fecha: {fecha_creacion} - Total: ${venta.total}')
    
    print('\n📊 Estadísticas de fechas:')
    print('=' * 60)
    
    # Fecha más antigua
    venta_antigua = Sale.objects.order_by('created_at').first()
    if venta_antigua:
        print(f'Venta más antigua: {venta_antigua.created_at.strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Fecha más reciente
    venta_reciente = Sale.objects.order_by('-created_at').first()
    if venta_reciente:
        print(f'Venta más reciente: {venta_reciente.created_at.strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Ventas por año
    ventas_por_ano = Sale.objects.extra(
        select={'year': 'strftime("%%Y", created_at)'}
    ).values('year').annotate(
        total=Count('id')
    ).order_by('year')
    
    print('\n📅 Ventas por año:')
    for venta_ano in ventas_por_ano:
        print(f'  {venta_ano["year"]}: {venta_ano["total"]} ventas')
    
    # Ventas por mes (últimos 12 meses)
    from datetime import datetime, timedelta
    fecha_limite = datetime.now() - timedelta(days=365)
    
    ventas_por_mes = Sale.objects.filter(
        created_at__gte=timezone.make_aware(fecha_limite)
    ).extra(
        select={'month': 'strftime("%%Y-%%m", created_at)'}
    ).values('month').annotate(
        total=Count('id')
    ).order_by('month')
    
    print('\n📅 Ventas por mes (últimos 12 meses):')
    for venta_mes in ventas_por_mes:
        print(f'  {venta_mes["month"]}: {venta_mes["total"]} ventas')
    
    # Verificar que las fechas estén distribuidas correctamente
    print('\n🔍 Verificación de distribución temporal:')
    print('=' * 60)
    
    # Contar ventas por año
    ventas_2023 = Sale.objects.filter(created_at__year=2023).count()
    ventas_2024 = Sale.objects.filter(created_at__year=2024).count()
    ventas_2025 = Sale.objects.filter(created_at__year=2025).count()
    
    print(f'Ventas en 2023: {ventas_2023}')
    print(f'Ventas en 2024: {ventas_2024}')
    print(f'Ventas en 2025: {ventas_2025}')
    
    total_ventas = Sale.objects.count()
    print(f'Total de ventas: {total_ventas}')
    
    if total_ventas > 0:
        print(f'Distribución:')
        print(f'  2023: {(ventas_2023/total_ventas)*100:.1f}%')
        print(f'  2024: {(ventas_2024/total_ventas)*100:.1f}%')
        print(f'  2025: {(ventas_2025/total_ventas)*100:.1f}%')

if __name__ == '__main__':
    verificar_fechas_ventas()
