from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import Company

User = get_user_model()


class Command(BaseCommand):
    help = 'Crear usuario administrador y datos iniciales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Nombre de usuario del admin'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@SmartSales365.com',
            help='Email del admin'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Contraseña del admin'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Crear usuario admin
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'El usuario {username} ya existe')
            )
        else:
            admin_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Administrador',
                last_name='Sistema',
                role='admin',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Usuario admin creado: {username}')
            )

        # Crear información de empresa por defecto
        if not Company.objects.exists():
            Company.objects.create(
                name='SmartSales365',
                legal_name='SmartSales365 S.A. de C.V.',
                rfc='SSA123456789',
                address='Av. Tecnología 123, Col. Digital, CDMX',
                phone='+52 55 1234 5678',
                email='info@SmartSales365.com',
                website='https://SmartSales365.com',
                tax_rate=16.0,
                currency='MXN',
                timezone='America/Mexico_City'
            )
            self.stdout.write(
                self.style.SUCCESS('Información de empresa creada')
            )

        # Crear algunos datos de ejemplo
        self.create_sample_data()

        self.stdout.write(
            self.style.SUCCESS('Datos iniciales creados exitosamente')
        )

    def create_sample_data(self):
        """Crear datos de ejemplo"""
        from apps.products.models import Category, Product
        from apps.clients.models import Client

        # Crear categorías de ejemplo
        if not Category.objects.exists():
            categories = [
                {'name': 'Electrónicos', 'description': 'Dispositivos electrónicos'},
                {'name': 'Ropa', 'description': 'Vestimenta y accesorios'},
                {'name': 'Hogar', 'description': 'Artículos para el hogar'},
                {'name': 'Deportes', 'description': 'Artículos deportivos'},
            ]
            
            for cat_data in categories:
                Category.objects.create(**cat_data)
            
            self.stdout.write('Categorías de ejemplo creadas')

        # Crear productos de ejemplo
        if not Product.objects.exists():
            electronics = Category.objects.get(name='Electrónicos')
            products = [
                {
                    'name': 'Laptop HP Pavilion',
                    'description': 'Laptop HP Pavilion 15 pulgadas, Intel i5, 8GB RAM',
                    'sku': 'LAP-HP-001',
                    'price': 15000.00,
                    'cost': 12000.00,
                    'stock': 10,
                    'category': electronics,
                    'barcode': '1234567890123'
                },
                {
                    'name': 'Smartphone Samsung Galaxy',
                    'description': 'Smartphone Samsung Galaxy A54, 128GB, 6GB RAM',
                    'sku': 'SPH-SAM-001',
                    'price': 8000.00,
                    'cost': 6000.00,
                    'stock': 25,
                    'category': electronics,
                    'barcode': '1234567890124'
                },
                {
                    'name': 'Auriculares Bluetooth',
                    'description': 'Auriculares inalámbricos con cancelación de ruido',
                    'sku': 'AUR-BT-001',
                    'price': 2000.00,
                    'cost': 1200.00,
                    'stock': 50,
                    'category': electronics,
                    'barcode': '1234567890125'
                }
            ]
            
            for prod_data in products:
                Product.objects.create(**prod_data)
            
            self.stdout.write('Productos de ejemplo creados')

        # Crear clientes de ejemplo
        if not Client.objects.exists():
            clients = [
                {
                    'name': 'Juan Pérez',
                    'email': 'juan.perez@email.com',
                    'phone': '555-1234',
                    'address': 'Calle Principal 123, Col. Centro',
                    'city': 'Ciudad de México',
                    'client_type': 'individual',
                    'segment': 'regular'
                },
                {
                    'name': 'María García',
                    'email': 'maria.garcia@email.com',
                    'phone': '555-5678',
                    'address': 'Av. Reforma 456, Col. Juárez',
                    'city': 'Ciudad de México',
                    'client_type': 'individual',
                    'segment': 'vip'
                },
                {
                    'name': 'Empresa ABC S.A.',
                    'email': 'contacto@empresaabc.com',
                    'phone': '555-9999',
                    'address': 'Blvd. Insurgentes 789, Col. Roma',
                    'city': 'Ciudad de México',
                    'client_type': 'business',
                    'segment': 'regular'
                }
            ]
            
            for client_data in clients:
                Client.objects.create(**client_data)
            
            self.stdout.write('Clientes de ejemplo creados')
