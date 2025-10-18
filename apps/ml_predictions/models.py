from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel
import uuid

class MLModel(BaseModel):
    """Modelos de Machine Learning"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Nombre')
    model_type = models.CharField(max_length=50, choices=[
        ('sales_forecast', 'Pronóstico de Ventas'),
        ('customer_segmentation', 'Segmentación de Clientes'),
        ('recommendation', 'Sistema de Recomendaciones'),
        ('churn_prediction', 'Predicción de Abandono'),
        ('demand_forecast', 'Pronóstico de Demanda'),
        ('price_optimization', 'Optimización de Precios')
    ], verbose_name='Tipo de Modelo')
    model_file = models.CharField(max_length=500, verbose_name='Archivo del Modelo')
    accuracy = models.FloatField(null=True, blank=True, verbose_name='Precisión')
    r2_score = models.FloatField(null=True, blank=True, verbose_name='R² Score')
    mae = models.FloatField(null=True, blank=True, verbose_name='MAE')
    rmse = models.FloatField(null=True, blank=True, verbose_name='RMSE')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    version = models.CharField(max_length=20, default='1.0', verbose_name='Versión')
    training_data_size = models.PositiveIntegerField(null=True, blank=True, verbose_name='Tamaño de Datos de Entrenamiento')
    features_used = models.JSONField(default=list, verbose_name='Features Utilizadas')
    hyperparameters = models.JSONField(default=dict, verbose_name='Hiperparámetros')
    training_date = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Entrenamiento')
    last_retrain = models.DateTimeField(null=True, blank=True, verbose_name='Último Reentrenamiento')
    
    class Meta:
        verbose_name = 'Modelo ML'
        verbose_name_plural = 'Modelos ML'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class Prediction(BaseModel):
    """Predicciones del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, verbose_name='Modelo')
    input_data = models.JSONField(verbose_name='Datos de Entrada')
    prediction_result = models.JSONField(verbose_name='Resultado de Predicción')
    confidence = models.FloatField(null=True, blank=True, verbose_name='Confianza')
    prediction_date = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Predicción')
    target_date = models.DateField(null=True, blank=True, verbose_name='Fecha Objetivo')
    category = models.CharField(max_length=100, blank=True, verbose_name='Categoría')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    
    class Meta:
        verbose_name = 'Predicción'
        verbose_name_plural = 'Predicciones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Predicción {self.id} - {self.model.name}"


class ModelTrainingLog(BaseModel):
    """Log de entrenamiento de modelos"""
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, verbose_name='Modelo')
    training_type = models.CharField(max_length=20, choices=[
        ('initial', 'Inicial'),
        ('retrain', 'Reentrenamiento'),
        ('update', 'Actualización')
    ], verbose_name='Tipo de Entrenamiento')
    status = models.CharField(max_length=20, choices=[
        ('started', 'Iniciado'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido')
    ], verbose_name='Estado')
    training_data_size = models.PositiveIntegerField(verbose_name='Tamaño de Datos')
    accuracy_before = models.FloatField(null=True, blank=True, verbose_name='Precisión Antes')
    accuracy_after = models.FloatField(null=True, blank=True, verbose_name='Precisión Después')
    training_duration = models.DurationField(null=True, blank=True, verbose_name='Duración del Entrenamiento')
    error_message = models.TextField(blank=True, verbose_name='Mensaje de Error')
    parameters_used = models.JSONField(default=dict, verbose_name='Parámetros Utilizados')
    
    class Meta:
        verbose_name = 'Log de Entrenamiento'
        verbose_name_plural = 'Logs de Entrenamiento'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Entrenamiento {self.model.name} - {self.get_status_display()}"


class FeatureImportance(BaseModel):
    """Importancia de features en modelos"""
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, verbose_name='Modelo')
    feature_name = models.CharField(max_length=100, verbose_name='Nombre del Feature')
    importance_score = models.FloatField(verbose_name='Score de Importancia')
    rank = models.PositiveIntegerField(verbose_name='Ranking')
    
    class Meta:
        verbose_name = 'Importancia de Feature'
        verbose_name_plural = 'Importancia de Features'
        ordering = ['rank']
    
    def __str__(self):
        return f"{self.feature_name} - {self.importance_score:.4f}"
