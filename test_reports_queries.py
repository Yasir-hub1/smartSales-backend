#!/usr/bin/env python
"""
Script de prueba para verificar el sistema de reportes
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.reports.services import DynamicReportGenerator, ReportPromptParser
from apps.sales.models import Sale
from django.utils import timezone
from datetime import datetime

def test_parser():
    """Prueba el parser con diferentes prompts"""
    print("=" * 80)
    print("PRUEBAS DEL PARSER DE PROMPTS")
    print("=" * 80)
    
    parser = ReportPromptParser()
    
    test_prompts = [
        "ventas de octubre",
        "dame la lista de ventas de octubre",
        "ventas del mes actual",
        "ventas de noviembre",
        "ventas de diciembre",
        "ventas de enero",
        "ventas de este mes",
        "ventas de septiembre",
    ]
    
    for prompt in test_prompts:
        separator = '=' * 80
        print(f"\n{separator}")
        print(f"PROMPT: '{prompt}'")
        print(separator)
        result = parser.parse_prompt(prompt)
        print(f"Resultado:")
        print(f"  - Tipo: {result['type']}")
        print(f"  - Date range: {result.get('date_range')}")
        print(f"  - Specific date: {result.get('specific_date')}")
        print(f"  - Group by: {result.get('group_by')}")
        print(f"  - Format: {result.get('format')}")

def test_report_generation():
    """Prueba la generación de reportes con diferentes prompts"""
    print("\n" + "=" * 80)
    print("PRUEBAS DE GENERACIÓN DE REPORTES")
    print("=" * 80)
    
    generator = DynamicReportGenerator()
    
    # Primero, verificar qué ventas hay en la base de datos
    print("\n📊 VENTAS EN LA BASE DE DATOS:")
    all_sales = Sale.objects.all().order_by('-created_at')
    print(f"Total de ventas: {all_sales.count()}")
    
    if all_sales.exists():
        print("\nÚltimas 10 ventas:")
        for sale in all_sales[:10]:
            print(f"  - ID: {sale.id}")
            print(f"    Fecha: {sale.created_at.date()} ({sale.created_at})")
            print(f"    Cliente: {sale.client.name if sale.client else 'Anónimo'}")
            print(f"    Total: {sale.total}")
            print()
    
    # Obtener el mes actual
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    
    print(f"\n📅 FECHA ACTUAL: {now.date()} (Mes: {current_month}, Año: {current_year})")
    
    # Probar diferentes consultas
    test_prompts = [
        ("ventas de octubre", "Debería traer solo ventas de octubre"),
        ("dame la lista de ventas de octubre", "Debería traer solo ventas de octubre"),
        ("ventas del mes actual", f"Debería traer solo ventas de {current_month} (mes actual)"),
        ("ventas de noviembre", "Debería traer solo ventas de noviembre"),
    ]
    
    for prompt, expected in test_prompts:
        separator = '=' * 80
        print(f"\n{separator}")
        print(f"PROMPT: '{prompt}'")
        print(f"ESPERADO: {expected}")
        print(separator)
        
        try:
            result = generator.generate_report(prompt, 'screen')
            
            if isinstance(result, list):
                print(f"\n✅ Resultado: {len(result)} ventas encontradas")
                if len(result) > 0:
                    print("\nPrimeras 5 ventas:")
                    for i, sale in enumerate(result[:5], 1):
                        print(f"  {i}. {sale}")
                else:
                    print("⚠️ No se encontraron ventas")
            else:
                print(f"\n⚠️ Resultado inesperado: {type(result)}")
                print(f"   Contenido: {result}")
                
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

def test_date_filtering():
    """Prueba específica del filtrado por fecha"""
    print("\n" + "=" * 80)
    print("PRUEBAS DE FILTRADO POR FECHA")
    print("=" * 80)
    
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Obtener todas las ventas agrupadas por mes
    print("\n📊 VENTAS POR MES:")
    all_sales = Sale.objects.all()
    
    from collections import defaultdict
    sales_by_month = defaultdict(list)
    
    for sale in all_sales:
        month_key = sale.created_at.strftime('%Y-%m')
        sales_by_month[month_key].append(sale)
    
    for month_key in sorted(sales_by_month.keys()):
        sales = sales_by_month[month_key]
        print(f"  {month_key}: {len(sales)} ventas")
        if len(sales) > 0:
            first_date = min(s.created_at.date() for s in sales)
            last_date = max(s.created_at.date() for s in sales)
            print(f"    Rango: {first_date} a {last_date}")
    
    # Probar filtros específicos
    print("\n🔍 PRUEBAS DE FILTROS ESPECÍFICOS:")
    
    # Octubre 2025
    oct_start = timezone.make_aware(datetime(2025, 10, 1, 0, 0, 0))
    oct_end = timezone.make_aware(datetime(2025, 11, 1, 0, 0, 0))
    oct_sales = Sale.objects.filter(
        created_at__gte=oct_start,
        created_at__lt=oct_end
    )
    print(f"\nOctubre 2025 (directo): {oct_sales.count()} ventas")
    if oct_sales.exists():
        for sale in oct_sales[:3]:
            print(f"  - {sale.created_at.date()} - {sale.client.name if sale.client else 'Anónimo'} - ${sale.total}")
    
    # Noviembre 2025
    nov_start = timezone.make_aware(datetime(2025, 11, 1, 0, 0, 0))
    nov_end = timezone.make_aware(datetime(2025, 12, 1, 0, 0, 0))
    nov_sales = Sale.objects.filter(
        created_at__gte=nov_start,
        created_at__lt=nov_end
    )
    print(f"\nNoviembre 2025 (directo): {nov_sales.count()} ventas")
    if nov_sales.exists():
        for sale in nov_sales[:3]:
            print(f"  - {sale.created_at.date()} - {sale.client.name if sale.client else 'Anónimo'} - ${sale.total}")

if __name__ == '__main__':
    print("\n🚀 INICIANDO PRUEBAS DEL SISTEMA DE REPORTES\n")
    
    # Ejecutar pruebas
    test_parser()
    test_date_filtering()
    test_report_generation()
    
    print("\n" + "=" * 80)
    print("PRUEBAS COMPLETADAS")
    print("=" * 80)

