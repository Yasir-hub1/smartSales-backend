from django.core.management.base import BaseCommand
from apps.payments.models import PaymentMethod

class Command(BaseCommand):
    help = 'Crear métodos de pago por defecto'

    def handle(self, *args, **options):
        # Métodos de pago por defecto
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
                self.stdout.write(f'✓ Creado: {method.name}')
            else:
                self.stdout.write(f'→ Ya existe: {method.name}')
        
        self.stdout.write(f"\nTotal de métodos de pago: {PaymentMethod.objects.count()}")
