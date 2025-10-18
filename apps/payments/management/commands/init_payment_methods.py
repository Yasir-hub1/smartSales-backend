from django.core.management.base import BaseCommand
from apps.payments.models import PaymentMethod
from apps.payments.stripe_config import DEFAULT_PAYMENT_METHODS


class Command(BaseCommand):
    help = 'Inicializar métodos de pago por defecto'

    def handle(self, *args, **options):
        self.stdout.write('Inicializando métodos de pago...')
        
        for method_data in DEFAULT_PAYMENT_METHODS:
            method, created = PaymentMethod.objects.get_or_create(
                code=method_data['code'],
                defaults=method_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Método de pago creado: {method.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Método de pago ya existe: {method.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Métodos de pago inicializados correctamente')
        )
