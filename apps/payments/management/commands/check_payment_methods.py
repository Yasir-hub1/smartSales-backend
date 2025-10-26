from django.core.management.base import BaseCommand
from apps.payments.models import PaymentMethod

class Command(BaseCommand):
    help = 'Verificar métodos de pago en la base de datos'

    def handle(self, *args, **options):
        methods = PaymentMethod.objects.all()
        
        if methods.exists():
            self.stdout.write(f'Se encontraron {methods.count()} métodos de pago:')
            for method in methods:
                self.stdout.write(f'- {method.name} ({method.code}) - Activo: {method.is_active}')
        else:
            self.stdout.write('No se encontraron métodos de pago en la base de datos')
            self.stdout.write('Creando métodos de pago por defecto...')
            
            # Crear métodos de pago por defecto
            default_methods = [
                {
                    'name': 'Tarjeta de Crédito/Débito',
                    'code': 'stripe',
                    'is_active': True,
                    'is_online': True,
                    'icon': 'credit-card',
                    'description': 'Pago seguro con tarjeta de crédito o débito',
                    'sort_order': 1
                },
                {
                    'name': 'Efectivo',
                    'code': 'cash',
                    'is_active': True,
                    'is_online': False,
                    'icon': 'money-bill',
                    'description': 'Pago en efectivo al recibir el producto',
                    'sort_order': 2
                },
                {
                    'name': 'Transferencia Bancaria',
                    'code': 'transfer',
                    'is_active': True,
                    'is_online': False,
                    'icon': 'university',
                    'description': 'Transferencia bancaria directa',
                    'sort_order': 3
                }
            ]
            
            for method_data in default_methods:
                method, created = PaymentMethod.objects.get_or_create(
                    code=method_data['code'],
                    defaults=method_data
                )
                if created:
                    self.stdout.write(f'Creado: {method.name}')
                else:
                    self.stdout.write(f'Ya existe: {method.name}')
