#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Seeder inteligente para generar datos coherentes de ventas
Específicamente diseñado para mejorar las predicciones de ML
Genera datos de los últimos 6 meses con patrones realistas
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
import numpy as np
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.db import transaction
from django.utils import timezone
from apps.core.models import User
from apps.products.models import Product
from apps.clients.models import Client
from apps.sales.models import Sale, SaleItem

class SalesPatternGenerator:
    """Generador de patrones de ventas realistas"""
    
    def __init__(self):
        self.base_daily_sales = 15000  # Ventas base diarias
        self.seasonal_multipliers = {
            1: 0.8,   # Enero - bajo (post-navidad)
            2: 0.9,   # Febrero - bajo
            3: 1.1,   # Marzo - medio (inicio primavera)
            4: 1.2,   # Abril - alto (vacaciones)
            5: 1.3,   # Mayo - alto (día de las madres)
            6: 1.1,   # Junio - medio
            7: 1.0,   # Julio - medio
            8: 0.9,   # Agosto - bajo (vacaciones)
            9: 1.1,   # Septiembre - medio (regreso a clases)
            10: 1.2,  # Octubre - alto
            11: 1.4,  # Noviembre - muy alto (buen fin)
            12: 1.5   # Diciembre - muy alto (navidad)
        }
        
        # Patrones por día de la semana
        self.weekly_patterns = {
            0: 1.0,   # Lunes
            1: 1.1,   # Martes
            2: 1.2,   # Miércoles
            3: 1.3,   # Jueves
            4: 1.4,   # Viernes
            5: 1.6,   # Sábado
            6: 1.2    # Domingo
        }
        
        # Días festivos mexicanos
        self.holidays = [
            (1, 1),   # Año Nuevo
            (2, 5),   # Día de la Constitución
            (3, 21),  # Natalicio de Benito Juárez
            (5, 1),   # Día del Trabajo
            (9, 16), # Día de la Independencia
            (11, 20), # Día de la Revolución
            (12, 25), # Navidad
        ]
    
    def is_holiday(self, date):
        """Verifica si es día festivo"""
        return (date.month, date.day) in self.holidays
    
    def get_seasonal_multiplier(self, month):
        """Obtiene multiplicador estacional"""
        return self.seasonal_multipliers.get(month, 1.0)
    
    def get_weekly_multiplier(self, weekday):
        """Obtiene multiplicador por día de la semana"""
        return self.weekly_patterns.get(weekday, 1.0)
    
    def calculate_daily_sales(self, date):
        """Calcula ventas esperadas para un día específico"""
        # Multiplicador estacional
        seasonal = self.get_seasonal_multiplier(date.month)
        
        # Multiplicador por día de la semana
        weekly = self.get_weekly_multiplier(date.weekday())
        
        # Multiplicador por festivo
        holiday = 0.3 if self.is_holiday(date) else 1.0
        
        # Agregar ruido aleatorio
        noise = np.random.normal(1.0, 0.15)
        
        # Calcular ventas del día
        daily_sales = self.base_daily_sales * seasonal * weekly * holiday * noise
        
        return max(0, daily_sales)
    
    def generate_sales_for_date(self, date, clients, products, users):
        """Genera ventas para una fecha específica"""
        expected_sales = self.calculate_daily_sales(date)
        
        # Número de transacciones (distribución de Poisson)
        num_transactions = max(1, int(np.random.poisson(expected_sales / 2000)))
        
        sales_created = []
        
        for _ in range(num_transactions):
            # Cliente aleatorio
            client = random.choice(clients)
            
            # Usuario aleatorio (vendedor)
            user = random.choice(users)
            
            # Productos aleatorios (1-4 productos por venta)
            num_products = random.randint(1, 4)
            sale_products = random.sample(products, num_products)
            
            # Calcular totales
            subtotal = Decimal('0')
            items_data = []
            
            for product in sale_products:
                quantity = random.randint(1, 3)
                price = product.price
                item_subtotal = price * quantity
                subtotal += item_subtotal
                
                items_data.append({
                    'product': product,
                    'quantity': quantity,
                    'price': price,
                    'subtotal': item_subtotal
                })
            
            # Impuestos (16%)
            tax = subtotal * Decimal('0.16')
            
            # Descuento aleatorio (0-15%)
            discount_pct = random.randint(0, 15)
            discount = subtotal * Decimal(str(discount_pct / 100))
            
            # Total final
            total = subtotal + tax - discount
            
            # Estado de la venta
            status = random.choices(
                ['completed', 'pending', 'cancelled'],
                weights=[85, 12, 3]
            )[0]
            
            payment_status = 'paid' if status == 'completed' else 'pending'
            
            # Crear venta
            sale_datetime = timezone.make_aware(
                datetime.combine(date, datetime.min.time().replace(
                    hour=random.randint(9, 18),
                    minute=random.randint(0, 59)
                ))
            )
            
            sale = Sale.objects.create(
                client=client,
                user=user,
                subtotal=subtotal,
                tax=tax,
                discount=discount,
                total=total,
                status=status,
                payment_status=payment_status,
                notes=f"Venta generada para ML - {date.strftime('%Y-%m-%d')}",
                transaction_id=f"ML-{random.randint(100000, 999999)}"
            )
            
            # Actualizar fechas
            sale.created_at = sale_datetime
            sale.updated_at = sale_datetime
            sale.save(update_fields=['created_at', 'updated_at'])
            
            # Crear items
            for item_data in items_data:
                item = SaleItem.objects.create(
                    sale=sale,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                item.created_at = sale_datetime
                item.updated_at = sale_datetime
                item.save(update_fields=['created_at', 'updated_at'])
            
            # Actualizar estadísticas del cliente
            if status == 'completed':
                client.total_purchases += total
                if not client.last_purchase_date or sale_datetime > client.last_purchase_date:
                    client.last_purchase_date = sale_datetime
                client.save()
            
            sales_created.append(sale)
        
        return sales_created

def generar_ventas_ml_coherentes():
    """Genera ventas coherentes para los últimos 6 meses"""
    print("🤖 Generando ventas coherentes para ML...")
    print("=" * 60)
    
    # Obtener datos existentes
    clients = list(Client.objects.all())
    products = list(Product.objects.all())
    users = list(User.objects.filter(role__in=['seller', 'manager']))
    
    if not clients or not products or not users:
        print("❌ No hay suficientes datos base para generar ventas")
        return []
    
    print(f"📊 Datos base encontrados:")
    print(f"  👥 Clientes: {len(clients)}")
    print(f"  📦 Productos: {len(products)}")
    print(f"  👤 Usuarios: {len(users)}")
    
    # Generador de patrones
    generator = SalesPatternGenerator()
    
    # Fecha de inicio: 6 meses atrás
    start_date = timezone.now().date() - timedelta(days=180)
    end_date = timezone.now().date()
    
    print(f"\n📅 Generando ventas desde {start_date} hasta {end_date}")
    
    all_sales = []
    current_date = start_date
    
    while current_date <= end_date:
        # Generar ventas para el día
        daily_sales = generator.generate_sales_for_date(
            current_date, clients, products, users
        )
        all_sales.extend(daily_sales)
        
        # Mostrar progreso cada 30 días
        if (current_date - start_date).days % 30 == 0:
            days_passed = (current_date - start_date).days
            print(f"  📅 Progreso: {days_passed}/180 días - {len(daily_sales)} ventas generadas")
        
        current_date += timedelta(days=1)
    
    print(f"\n✅ Total de ventas generadas: {len(all_sales)}")
    return all_sales

def mostrar_estadisticas_ml():
    """Muestra estadísticas específicas para ML"""
    print("\n📊 ESTADÍSTICAS PARA MACHINE LEARNING")
    print("=" * 50)
    
    from django.db.models import Count, Sum, Avg
    
    # Ventas por mes (últimos 6 meses)
    fecha_6_meses = timezone.now() - timedelta(days=180)
    ventas_6_meses = Sale.objects.filter(created_at__gte=fecha_6_meses)
    
    print(f"📅 Ventas últimos 6 meses: {ventas_6_meses.count()}")
    
    # Estadísticas por mes
    meses_stats = []
    current_date = timezone.now().date() - timedelta(days=180)
    
    for i in range(6):
        month_start = current_date.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
        
        ventas_mes = ventas_6_meses.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        )
        
        total_ventas = ventas_mes.count()
        total_monto = ventas_mes.aggregate(Sum('total'))['total__sum'] or 0
        avg_venta = ventas_mes.aggregate(Avg('total'))['total__avg'] or 0
        
        meses_stats.append({
            'mes': month_start.strftime('%Y-%m'),
            'ventas': total_ventas,
            'monto': total_monto,
            'promedio': avg_venta
        })
        
        print(f"  {month_start.strftime('%Y-%m')}: {total_ventas} ventas - ${total_monto:,.2f} (avg: ${avg_venta:,.2f})")
        
        # Siguiente mes
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Estadísticas generales
    total_ventas = Sale.objects.count()
    total_ingresos = Sale.objects.aggregate(Sum('total'))['total__sum'] or 0
    avg_venta = Sale.objects.aggregate(Avg('total'))['total__avg'] or 0
    
    print(f"\n📊 Estadísticas Generales:")
    print(f"  💰 Total de ventas: {total_ventas}")
    print(f"  💵 Total de ingresos: ${total_ingresos:,.2f}")
    print(f"  📈 Promedio por venta: ${avg_venta:,.2f}")
    
    # Ventas por día de la semana
    print(f"\n📅 Ventas por día de la semana:")
    dias_semana = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    
    for i, dia in enumerate(dias_semana):
        ventas_dia = Sale.objects.extra(
            where=['strftime("%%w", created_at) = ?'],
            params=[str(i)]
        ).count()
        print(f"  {dia}: {ventas_dia} ventas")

def main():
    """Función principal"""
    print("🚀 GENERADOR DE DATOS COHERENTES PARA ML")
    print("=" * 60)
    print("Este script genera ventas realistas de los últimos 6 meses")
    print("con patrones coherentes para mejorar las predicciones de ML")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # Generar ventas coherentes
            sales = generar_ventas_ml_coherentes()
            
            # Mostrar estadísticas
            mostrar_estadisticas_ml()
            
        print("\n" + "=" * 60)
        print("✅ GENERACIÓN COMPLETADA EXITOSAMENTE!")
        print("🤖 Los datos están listos para entrenar el modelo de ML")
        print("📊 Ahora puedes ejecutar el entrenamiento del modelo")
        
    except Exception as e:
        print(f"❌ Error durante la generación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
