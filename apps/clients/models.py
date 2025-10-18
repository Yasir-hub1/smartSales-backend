from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Client(BaseModel):
    """Clientes del sistema"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    address = models.TextField(blank=True, verbose_name='Dirección')
    city = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    country = models.CharField(max_length=100, default='México', verbose_name='País')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='Código Postal')
    client_type = models.CharField(
        max_length=20, 
        choices=[
            ('individual', 'Individual'), 
            ('business', 'Empresa')
        ], 
        default='individual',
        verbose_name='Tipo de Cliente'
    )
    segment = models.CharField(
        max_length=20,
        choices=[
            ('vip', 'VIP'),
            ('regular', 'Regular'),
            ('new', 'Nuevo')
        ],
        default='new',
        verbose_name='Segmento'
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    notes = models.TextField(blank=True, verbose_name='Notas')
    avatar = models.ImageField(upload_to='clients/avatars/', blank=True, verbose_name='Avatar')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    last_purchase_date = models.DateTimeField(null=True, blank=True, verbose_name='Última Compra')
    total_purchases = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total de Compras')
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_address(self):
        """Dirección completa"""
        parts = [self.address, self.city, self.country]
        return ', '.join(filter(None, parts))
    
    @property
    def is_vip(self):
        """Verifica si es cliente VIP"""
        return self.segment == 'vip'
