from django.core.management.base import BaseCommand
from django.db import models
from apps.sales.models import Cart

class Command(BaseCommand):
    help = 'Limpiar carritos duplicados'

    def handle(self, *args, **options):
        self.stdout.write('Limpiando carritos duplicados...')
        
        # Limpiar carritos de usuarios autenticados
        users_with_multiple_carts = Cart.objects.filter(
            user__isnull=False,
            is_active=True
        ).values('user').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        
        for user_data in users_with_multiple_carts:
            user_id = user_data['user']
            carts = Cart.objects.filter(
                user_id=user_id,
                is_active=True
            ).order_by('-created_at')
            
            # Mantener el más reciente y desactivar los otros
            latest_cart = carts.first()
            old_carts = carts.exclude(id=latest_cart.id)
            
            self.stdout.write(f'Usuario {user_id}: Manteniendo carrito {latest_cart.id}, desactivando {old_carts.count()} carritos')
            old_carts.update(is_active=False)
        
        # Limpiar carritos de sesiones anónimas
        sessions_with_multiple_carts = Cart.objects.filter(
            user__isnull=True,
            is_active=True
        ).values('session_key').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        
        for session_data in sessions_with_multiple_carts:
            session_key = session_data['session_key']
            carts = Cart.objects.filter(
                session_key=session_key,
                user__isnull=True,
                is_active=True
            ).order_by('-created_at')
            
            # Mantener el más reciente y desactivar los otros
            latest_cart = carts.first()
            old_carts = carts.exclude(id=latest_cart.id)
            
            self.stdout.write(f'Sesión {session_key}: Manteniendo carrito {latest_cart.id}, desactivando {old_carts.count()} carritos')
            old_carts.update(is_active=False)
        
        self.stdout.write(self.style.SUCCESS('Limpieza completada!'))
