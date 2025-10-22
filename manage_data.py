#!/usr/bin/env python
"""
Script de gestión de datos para SmartSales365
Permite limpiar, poblar y gestionar la base de datos
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.db import transaction
from apps.core.models import User, Company
from apps.products.models import Category, Product, PriceHistory
from apps.clients.models import Client
from apps.sales.models import Sale, SaleItem, Cart, CartItem
from apps.ml_predictions.models import MLModel, Prediction, ModelTrainingLog, FeatureImportance

def limpiar_base_datos():
    """Limpiar toda la base de datos (excepto usuarios admin)"""
    print("🧹 Limpiando base de datos...")
    
    with transaction.atomic():
        # Limpiar en orden para evitar problemas de foreign key
        print("  🗑️ Eliminando items de venta...")
        SaleItem.objects.all().delete()
        
        print("  🗑️ Eliminando ventas...")
        Sale.objects.all().delete()
        
        print("  🗑️ Eliminando items del carrito...")
        CartItem.objects.all().delete()
        
        print("  🗑️ Eliminando carritos...")
        Cart.objects.all().delete()
        
        print("  🗑️ Eliminando clientes...")
        Client.objects.all().delete()
        
        print("  🗑️ Eliminando historial de precios...")
        PriceHistory.objects.all().delete()
        
        print("  🗑️ Eliminando productos...")
        Product.objects.all().delete()
        
        print("  🗑️ Eliminando categorías...")
        Category.objects.all().delete()
        
        print("  🗑️ Eliminando modelos ML...")
        FeatureImportance.objects.all().delete()
        ModelTrainingLog.objects.all().delete()
        Prediction.objects.all().delete()
        MLModel.objects.all().delete()
        
        print("  🗑️ Eliminando empresa...")
        Company.objects.all().delete()
        
        # Mantener solo usuarios admin
        print("  👤 Manteniendo usuarios admin...")
        User.objects.exclude(username__in=['admin', 'gerente']).delete()
    
    print("✅ Base de datos limpiada exitosamente!")

def poblar_datos():
    """Poblar la base de datos con datos de electrodomésticos"""
    print("🌱 Poblando base de datos con datos de electrodomésticos...")
    
    # Ejecutar el seeder
    exec(open('seed_electrodomesticos.py').read())

def mostrar_estadisticas():
    """Mostrar estadísticas de la base de datos"""
    print("📊 Estadísticas de la base de datos:")
    print("=" * 50)
    
    try:
        print(f"🏢 Empresas: {Company.objects.count()}")
        print(f"👤 Usuarios: {User.objects.count()}")
        print(f"📁 Categorías: {Category.objects.count()}")
        print(f"📦 Productos: {Product.objects.count()}")
        print(f"👥 Clientes: {Client.objects.count()}")
        print(f"💰 Ventas: {Sale.objects.count()}")
        print(f"📋 Items de venta: {SaleItem.objects.count()}")
        print(f"🛒 Carritos: {Cart.objects.count()}")
        print(f"🤖 Modelos ML: {MLModel.objects.count()}")
        print(f"🔮 Predicciones: {Prediction.objects.count()}")
        
        # Estadísticas de ventas
        if Sale.objects.exists():
            ventas = Sale.objects.all()
            total_ventas = sum(venta.total for venta in ventas)
            ventas_completadas = ventas.filter(status='completed').count()
            
            print(f"\n💰 Total de ventas: ${total_ventas:,.2f}")
            print(f"✅ Ventas completadas: {ventas_completadas}")
            print(f"📈 Tasa de completitud: {(ventas_completadas/ventas.count())*100:.1f}%")
        
        # Productos más vendidos
        if SaleItem.objects.exists():
            from django.db.models import Sum
            productos_mas_vendidos = SaleItem.objects.values('product__name').annotate(
                total_vendido=Sum('quantity')
            ).order_by('-total_vendido')[:5]
            
            print(f"\n🏆 Top 5 productos más vendidos:")
            for i, item in enumerate(productos_mas_vendidos, 1):
                print(f"  {i}. {item['product__name']} - {item['total_vendido']} unidades")
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {str(e)}")

def reset_completo():
    """Reset completo: limpiar y poblar"""
    print("🔄 Realizando reset completo...")
    limpiar_base_datos()
    poblar_datos()
    mostrar_estadisticas()

def menu_principal():
    """Menú principal interactivo"""
    while True:
        print("\n" + "=" * 60)
        print("🏠 SmartSales365 - Gestión de Datos")
        print("=" * 60)
        print("1. 📊 Mostrar estadísticas")
        print("2. 🧹 Limpiar base de datos")
        print("3. 🌱 Poblar con datos de electrodomésticos")
        print("4. 🔄 Reset completo (limpiar + poblar)")
        print("5. 🚪 Salir")
        print("=" * 60)
        
        opcion = input("Selecciona una opción (1-5): ").strip()
        
        if opcion == '1':
            mostrar_estadisticas()
        elif opcion == '2':
            confirmar = input("⚠️ ¿Estás seguro de limpiar la base de datos? (sí/no): ")
            if confirmar.lower() in ['sí', 'si', 'yes', 'y']:
                limpiar_base_datos()
            else:
                print("❌ Operación cancelada")
        elif opcion == '3':
            poblar_datos()
            mostrar_estadisticas()
        elif opcion == '4':
            confirmar = input("⚠️ ¿Estás seguro del reset completo? (sí/no): ")
            if confirmar.lower() in ['sí', 'si', 'yes', 'y']:
                reset_completo()
            else:
                print("❌ Operación cancelada")
        elif opcion == '5':
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida. Intenta de nuevo.")

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == 'stats':
            mostrar_estadisticas()
        elif comando == 'clean':
            limpiar_base_datos()
        elif comando == 'seed':
            poblar_datos()
        elif comando == 'reset':
            reset_completo()
        else:
            print("❌ Comando no reconocido")
            print("Comandos disponibles: stats, clean, seed, reset")
    else:
        # Modo interactivo
        menu_principal()

if __name__ == '__main__':
    main()
