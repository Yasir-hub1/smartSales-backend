from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
import uuid

class Report(BaseModel):
    """Reportes del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    report_type = models.CharField(max_length=50, choices=[
        ('sales', 'Ventas'),
        ('products', 'Productos'),
        ('clients', 'Clientes'),
        ('financial', 'Financiero'),
        ('inventory', 'Inventario'),
        ('predictions', 'Predicciones')
    ], verbose_name='Tipo de Reporte')
    format = models.CharField(max_length=10, choices=[
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
        ('csv', 'CSV')
    ], default='pdf', verbose_name='Formato')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido')
    ], default='pending', verbose_name='Estado')
    parameters = models.JSONField(default=dict, verbose_name='Parámetros')
    prompt = models.TextField(blank=True, verbose_name='Prompt Original')
    source = models.CharField(max_length=10, choices=[
        ('text', 'Texto'),
        ('voice', 'Voz')
    ], default='text', verbose_name='Fuente')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='Ruta del archivo')
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name='Tamaño del archivo')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    generated_at = models.DateTimeField(null=True, blank=True, verbose_name='Generado en')
    error_message = models.TextField(blank=True, verbose_name='Mensaje de Error')
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"


class ReportTemplate(BaseModel):
    """Plantillas de reportes"""
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    report_type = models.CharField(max_length=50, choices=[
        ('sales', 'Ventas'),
        ('products', 'Productos'),
        ('clients', 'Clientes'),
        ('financial', 'Financiero')
    ], verbose_name='Tipo de Reporte')
    template_data = models.JSONField(verbose_name='Datos de Plantilla')
    is_public = models.BooleanField(default=False, verbose_name='Público')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    
    class Meta:
        verbose_name = 'Plantilla de Reporte'
        verbose_name_plural = 'Plantillas de Reportes'
    
    def __str__(self):
        return self.name


class ReportSchedule(BaseModel):
    """Programación de reportes"""
    name = models.CharField(max_length=200, verbose_name='Nombre')
    report_type = models.CharField(max_length=50, choices=[
        ('sales', 'Ventas'),
        ('products', 'Productos'),
        ('clients', 'Clientes'),
        ('financial', 'Financiero')
    ], verbose_name='Tipo de Reporte')
    parameters = models.JSONField(verbose_name='Parámetros')
    schedule_type = models.CharField(max_length=20, choices=[
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral')
    ], verbose_name='Tipo de Programación')
    schedule_time = models.TimeField(verbose_name='Hora de Ejecución')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    last_run = models.DateTimeField(null=True, blank=True, verbose_name='Última Ejecución')
    next_run = models.DateTimeField(null=True, blank=True, verbose_name='Próxima Ejecución')
    
    class Meta:
        verbose_name = 'Programación de Reporte'
        verbose_name_plural = 'Programaciones de Reportes'
    
    def __str__(self):
        return f"{self.name} - {self.get_schedule_type_display()}"
