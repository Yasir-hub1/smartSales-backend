from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class BaseModel(models.Model):
    """Modelo base con campos comunes"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        abstract = True


class User(AbstractUser):
    """Usuario personalizado del sistema"""
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    avatar = models.ImageField(upload_to='profiles/avatars/', blank=True, verbose_name='Avatar')
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Administrador'),
            ('manager', 'Gerente'),
            ('seller', 'Vendedor'),
            ('cashier', 'Cajero')
        ],
        default='seller',
        verbose_name='Rol'
    )
    is_online = models.BooleanField(default=False, verbose_name='En línea')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Última IP')
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name='Última Actividad')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    @property
    def full_name(self):
        """Nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def update_activity(self, ip_address=None):
        """Actualizar actividad del usuario"""
        self.last_activity = timezone.now()
        if ip_address:
            self.last_login_ip = ip_address
        self.save(update_fields=['last_activity', 'last_login_ip'])


class Company(BaseModel):
    """Información de la empresa"""
    name = models.CharField(max_length=200, default='SmartSales365', verbose_name='Nombre de la Empresa')
    legal_name = models.CharField(max_length=200, default='SmartSales365 S.A. de C.V.', verbose_name='Razón Social')
    rfc = models.CharField(max_length=13, default='SSA123456789', verbose_name='RFC')
    address = models.TextField(default='Av. Tecnología 123, Col. Digital, CDMX', verbose_name='Dirección')
    phone = models.CharField(max_length=20, default='+52 55 1234 5678', verbose_name='Teléfono')
    email = models.EmailField(default='info@smartsales365.com', verbose_name='Email')
    website = models.URLField(blank=True, default='https://smartsales365.com', verbose_name='Sitio Web')
    logo = models.ImageField(upload_to='company/logos/', blank=True, verbose_name='Logo')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=16.0, verbose_name='Tasa de Impuestos (%)')
    currency = models.CharField(max_length=3, default='MXN', verbose_name='Moneda')
    timezone = models.CharField(max_length=50, default='America/Mexico_City', verbose_name='Zona Horaria')
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
    
    def __str__(self):
        return self.name