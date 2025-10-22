"""
Comando para generar datos sintéticos de ventas para entrenamiento
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from apps.sales.models import Sale, SaleItem, Cart, CartItem
from apps.products.models import Product, Category
from apps.clients.models import Client
from apps.core.models import User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Genera datos sintéticos de ventas para entrenamiento del modelo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Número de días de datos a generar (default: 365)',
        )
        parser.add_argument(
            '--sales-per-day',
            type=int,
            default=20,
            help='Número promedio de ventas por día (default: 20)',
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Limpiar ventas existentes antes de generar nuevas',
        )

    def handle(self, *args, **options):
        days = options['days']
        sales_per_day = options['sales_per_day']
        clear_existing = options['clear_existing']
        
        if clear_existing:
            self.stdout.write('Limpiando ventas existentes...')
            Sale.objects.all().delete()
            self.stdout.write('✅ Ventas existentes eliminadas')
        
        # Verificar que existan productos y clientes
        if not Product.objects.exists():
            self.stdout.write('❌ No hay productos en la base de datos')
            self.stdout.write('Ejecuta primero: python manage.py setup_db')
            return
            
        if not Client.objects.exists():
            self.stdout.write('❌ No hay clientes en la base de datos')
            self.stdout.write('Ejecuta primero: python manage.py setup_db')
            return
        
        self.stdout.write(f'Generando {days} días de datos sintéticos...')
        self.stdout.write(f'Promedio de {sales_per_day} ventas por día')
        
        # Obtener productos y clientes
        products = list(Product.objects.filter(is_active=True))
        clients = list(Client.objects.all())
        
        if not products:
            self.stdout.write('❌ No hay productos activos')
            return
            
        if not clients:
            self.stdout.write('❌ No hay clientes')
            return
        
        # Generar ventas
        total_sales = 0
        start_date = timezone.now() - timedelta(days=days)
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Calcular número de ventas para este día (con variación)
            base_sales = sales_per_day
            
            # Variación por día de la semana
            weekday = current_date.weekday()
            if weekday >= 5:  # Fin de semana
                base_sales = int(base_sales * 1.5)
            elif weekday == 0:  # Lunes
                base_sales = int(base_sales * 0.8)
            
            # Variación estacional
            month = current_date.month
            if month in [11, 12]:  # Noviembre y diciembre
                base_sales = int(base_sales * 1.3)
            elif month in [1, 2]:  # Enero y febrero
                base_sales = int(base_sales * 0.7)
            
            # Agregar variación aleatoria
            daily_sales = max(1, int(base_sales * random.uniform(0.5, 1.5)))
            
            # Generar ventas para este día
            for _ in range(daily_sales):
                try:
                    # Seleccionar cliente aleatorio
                    client = random.choice(clients)
                    
                    # Crear venta
                    sale = Sale.objects.create(
                        client=client,
                        subtotal=Decimal('0.00'),
                        total=Decimal('0.00'),
                        status='completed',
                        payment_status='paid',
                        created_at=current_date + timedelta(
                            hours=random.randint(9, 18),
                            minutes=random.randint(0, 59)
                        )
                    )
                    
                    # Agregar productos a la venta
                    num_products = random.randint(1, 5)
                    selected_products = random.sample(products, min(num_products, len(products)))
                    
                    subtotal = Decimal('0.00')
                    for product in selected_products:
                        quantity = random.randint(1, 3)
                        price = product.price
                        item_total = price * quantity
                        
                        SaleItem.objects.create(
                            sale=sale,
                            product=product,
                            quantity=quantity,
                            price=price
                        )
                        
                        subtotal += item_total
                    
                    # Actualizar totales de la venta
                    sale.subtotal = subtotal
                    sale.total = subtotal
                    sale.save()
                    
                    total_sales += 1
                    
                except Exception as e:
                    self.stdout.write(f'Error creando venta: {str(e)}')
                    continue
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Generadas {total_sales} ventas sintéticas')
        )
        self.stdout.write(f'Período: {start_date.date()} a {timezone.now().date()}')
        
        # Mostrar estadísticas
        total_revenue = sum(sale.total for sale in Sale.objects.all())
        avg_sale = total_revenue / total_sales if total_sales > 0 else 0
        
        self.stdout.write(f'💰 Ingresos totales: ${total_revenue:,.2f}')
        self.stdout.write(f'📊 Venta promedio: ${avg_sale:,.2f}')
        self.stdout.write(f'📈 Ventas por día: {total_sales / days:.1f}')
