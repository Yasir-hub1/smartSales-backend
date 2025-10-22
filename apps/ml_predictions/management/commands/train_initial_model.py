"""
Comando para entrenar el modelo inicial de pronóstico de ventas
"""
from django.core.management.base import BaseCommand
from apps.ml_predictions.services import SalesForecastService
from apps.ml_predictions.models import MLModel
import os


class Command(BaseCommand):
    help = 'Entrena el modelo inicial de pronóstico de ventas con datos sintéticos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use-synthetic',
            action='store_true',
            help='Usar datos sintéticos para entrenamiento',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar reentrenamiento aunque ya exista un modelo',
        )

    def handle(self, *args, **options):
        use_synthetic = options['use_synthetic']
        force = options['force']
        
        # Verificar si ya existe un modelo
        existing_model = MLModel.objects.filter(
            model_type='sales_forecast',
            is_active=True
        ).first()
        
        if existing_model and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Ya existe un modelo activo: {existing_model.name} v{existing_model.version}'
                )
            )
            self.stdout.write('Usa --force para reentrenar')
            return
        
        self.stdout.write('Iniciando entrenamiento del modelo...')
        
        try:
            # Crear directorio de modelos si no existe
            os.makedirs('ml_models', exist_ok=True)
            
            # Entrenar modelo
            service = SalesForecastService()
            result = service.train_model(use_synthetic=use_synthetic)
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS('✅ Modelo entrenado exitosamente!')
                )
                self.stdout.write(f'R² Score: {result["r2_score"]:.4f}')
                self.stdout.write(f'MAE: {result["mae"]:.2f}')
                self.stdout.write(f'RMSE: {result["rmse"]:.2f}')
                self.stdout.write(f'CV Mean: {result["cv_mean"]:.4f} ± {result["cv_std"]:.4f}')
                
                # Mostrar importancia de features
                self.stdout.write('\n📊 Importancia de Features:')
                for i, feature in enumerate(result['feature_importance'][:5], 1):
                    self.stdout.write(f'{i}. {feature["feature"]}: {feature["importance"]:.4f}')
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error entrenando modelo: {result["error"]}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error inesperado: {str(e)}')
            )
