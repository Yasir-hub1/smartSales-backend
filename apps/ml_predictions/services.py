"""
Servicios de Machine Learning para SmartSales365
"""
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from apps.sales.models import Sale, SaleItem
from apps.products.models import Product, Category
from apps.clients.models import Client
from .models import MLModel, Prediction, ModelTrainingLog, FeatureImportance


class SalesForecastService:
    """Servicio de pronóstico de ventas usando Random Forest"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_path = 'ml_models/'
        
    def prepare_training_data(self, days_back: int = 365) -> pd.DataFrame:
        """Prepara datos de entrenamiento para el modelo"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Obtener datos de ventas
        sales_data = Sale.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            is_active=True
        ).select_related('client').prefetch_related('items__product')
        
        # Agregar datos por día
        daily_sales = []
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            day_sales = sales_data.filter(created_at__date=current_date)
            
            # Calcular features del día
            features = self._calculate_daily_features(day_sales, current_date)
            daily_sales.append(features)
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(daily_sales)
    
    def _calculate_daily_features(self, sales_queryset, date) -> Dict[str, Any]:
        """Calcula features para un día específico"""
        # Features básicas
        total_sales = sum(sale.total for sale in sales_queryset)
        num_transactions = sales_queryset.count()
        avg_transaction = total_sales / num_transactions if num_transactions > 0 else 0
        
        # Features temporales
        day_of_week = date.weekday()
        day_of_month = date.day
        month = date.month
        quarter = (month - 1) // 3 + 1
        is_weekend = day_of_week >= 5
        is_month_start = day_of_month <= 7
        is_month_end = day_of_month >= 25
        
        # Features de tendencia (últimos 7 días)
        week_ago = date - timedelta(days=7)
        week_sales = Sale.objects.filter(
            created_at__date__gte=week_ago,
            created_at__date__lt=date,
            is_active=True
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Features de estacionalidad
        is_holiday = self._is_holiday(date)
        season = self._get_season(month)
        
        # Features de clientes
        unique_clients = sales_queryset.values('client').distinct().count()
        
        return {
            'date': date,
            'total_sales': total_sales,
            'num_transactions': num_transactions,
            'avg_transaction': avg_transaction,
            'day_of_week': day_of_week,
            'day_of_month': day_of_month,
            'month': month,
            'quarter': quarter,
            'is_weekend': int(is_weekend),
            'is_month_start': int(is_month_start),
            'is_month_end': int(is_month_end),
            'week_sales': week_sales,
            'is_holiday': int(is_holiday),
            'season': season,
            'unique_clients': unique_clients
        }
    
    def _is_holiday(self, date) -> bool:
        """Verifica si es día festivo (simplificado)"""
        holidays = [
            (1, 1),   # Año Nuevo
            (2, 5),   # Día de la Constitución
            (3, 21),  # Natalicio de Benito Juárez
            (5, 1),   # Día del Trabajo
            (9, 16), # Día de la Independencia
            (11, 20), # Día de la Revolución
            (12, 25), # Navidad
        ]
        return (date.month, date.day) in holidays
    
    def _get_season(self, month: int) -> int:
        """Obtiene la estación del año"""
        if month in [12, 1, 2]:
            return 0  # Invierno
        elif month in [3, 4, 5]:
            return 1  # Primavera
        elif month in [6, 7, 8]:
            return 2  # Verano
        else:
            return 3  # Otoño
    
    def generate_synthetic_data(self, days: int = 365) -> pd.DataFrame:
        """Genera datos sintéticos para entrenamiento inicial"""
        data = []
        base_date = timezone.now().date() - timedelta(days=days)
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            
            # Simular patrones realistas
            day_of_week = current_date.weekday()
            month = current_date.month
            
            # Base sales con estacionalidad
            base_sales = 1000
            weekend_multiplier = 1.5 if day_of_week >= 5 else 1.0
            seasonal_multiplier = self._get_seasonal_multiplier(month)
            
            # Agregar ruido aleatorio
            noise = np.random.normal(0, 0.2)
            total_sales = base_sales * weekend_multiplier * seasonal_multiplier * (1 + noise)
            
            # Features del día
            features = {
                'date': current_date,
                'total_sales': max(0, total_sales),
                'num_transactions': max(1, int(np.random.poisson(20))),
                'avg_transaction': total_sales / max(1, int(np.random.poisson(20))),
                'day_of_week': day_of_week,
                'day_of_month': current_date.day,
                'month': month,
                'quarter': (month - 1) // 3 + 1,
                'is_weekend': int(day_of_week >= 5),
                'is_month_start': int(current_date.day <= 7),
                'is_month_end': int(current_date.day >= 25),
                'week_sales': max(0, total_sales * np.random.normal(1, 0.3)),
                'is_holiday': int(self._is_holiday(current_date)),
                'season': self._get_season(month),
                'unique_clients': max(1, int(np.random.poisson(15)))
            }
            
            data.append(features)
        
        return pd.DataFrame(data)
    
    def _get_seasonal_multiplier(self, month: int) -> float:
        """Obtiene multiplicador estacional"""
        seasonal_patterns = {
            1: 0.8,   # Enero - bajo
            2: 0.9,   # Febrero - bajo
            3: 1.1,   # Marzo - medio
            4: 1.2,   # Abril - alto
            5: 1.3,   # Mayo - alto
            6: 1.1,   # Junio - medio
            7: 1.0,   # Julio - medio
            8: 0.9,   # Agosto - bajo
            9: 1.1,   # Septiembre - medio
            10: 1.2,  # Octubre - alto
            11: 1.4,  # Noviembre - muy alto
            12: 1.5   # Diciembre - muy alto
        }
        return seasonal_patterns.get(month, 1.0)
    
    def train_model(self, use_synthetic: bool = False) -> Dict[str, Any]:
        """Entrena el modelo Random Forest"""
        try:
            # Preparar datos
            if use_synthetic:
                df = self.generate_synthetic_data()
            else:
                df = self.prepare_training_data()
            
            if df.empty:
                raise ValueError("No hay datos suficientes para entrenar")
            
            # Separar features y target
            feature_columns = [col for col in df.columns if col not in ['date', 'total_sales']]
            X = df[feature_columns].values
            y = df['total_sales'].values
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Escalar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Entrenar modelo
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                min_samples_split=5,
                min_samples_leaf=2,
                n_jobs=-1
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluar modelo
            y_pred = self.model.predict(X_test_scaled)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Validación cruzada
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
            
            # Guardar modelo
            self._save_model(feature_columns)
            
            return {
                'success': True,
                'r2_score': r2,
                'mae': mae,
                'rmse': rmse,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'feature_importance': self._get_feature_importance(feature_columns)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_model(self, feature_names: List[str]):
        """Guarda el modelo entrenado"""
        os.makedirs(self.model_path, exist_ok=True)
        
        # Guardar modelo
        model_filename = f"sales_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
        model_path = os.path.join(self.model_path, model_filename)
        joblib.dump(self.model, model_path)
        
        # Guardar scaler
        scaler_filename = f"scaler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
        scaler_path = os.path.join(self.model_path, scaler_filename)
        joblib.dump(self.scaler, scaler_path)
        
        self.feature_names = feature_names
        
        # Guardar en base de datos
        ml_model, created = MLModel.objects.get_or_create(
            name='Sales Forecast Model',
            model_type='sales_forecast',
            defaults={
                'model_file': model_filename,
                'features_used': feature_names,
                'hyperparameters': {
                    'n_estimators': 100,
                    'max_depth': 10,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2
                }
            }
        )
        
        if not created:
            ml_model.model_file = model_filename
            ml_model.save()
    
    def _get_feature_importance(self, feature_names: List[str]) -> List[Dict[str, Any]]:
        """Obtiene importancia de features"""
        importance = self.model.feature_importances_
        feature_importance = list(zip(feature_names, importance))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {'feature': name, 'importance': float(imp)}
            for name, imp in feature_importance
        ]
    
    def predict_sales(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Predice ventas futuras"""
        if not self.model:
            self._load_latest_model()
        
        if not self.model:
            raise ValueError("No hay modelo entrenado disponible")
        
        predictions = []
        current_date = timezone.now().date()
        
        for i in range(1, days_ahead + 1):
            target_date = current_date + timedelta(days=i)
            
            # Preparar features para la fecha objetivo
            features = self._prepare_prediction_features(target_date)
            
            # Escalar features
            features_scaled = self.scaler.transform([features])
            
            # Hacer predicción
            prediction = self.model.predict(features_scaled)[0]
            
            # Calcular intervalo de confianza (simplificado)
            confidence_interval = prediction * 0.1  # 10% de variación
            
            predictions.append({
                'date': target_date,
                'predicted_sales': max(0, prediction),
                'confidence_lower': max(0, prediction - confidence_interval),
                'confidence_upper': prediction + confidence_interval,
                'day_of_week': target_date.weekday(),
                'is_weekend': target_date.weekday() >= 5
            })
        
        return predictions
    
    def _prepare_prediction_features(self, target_date) -> List[float]:
        """Prepara features para una fecha específica"""
        # Obtener datos históricos para calcular tendencias
        week_ago = target_date - timedelta(days=7)
        recent_sales = Sale.objects.filter(
            created_at__date__gte=week_ago,
            created_at__date__lt=target_date,
            is_active=True
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Features temporales
        day_of_week = target_date.weekday()
        day_of_month = target_date.day
        month = target_date.month
        quarter = (month - 1) // 3 + 1
        is_weekend = day_of_week >= 5
        is_month_start = day_of_month <= 7
        is_month_end = day_of_month >= 25
        is_holiday = self._is_holiday(target_date)
        season = self._get_season(month)
        
        # Features estimadas (en producción se calcularían con datos reales)
        num_transactions = 20  # Estimación
        avg_transaction = recent_sales / max(1, num_transactions)
        unique_clients = 15  # Estimación
        
        return [
            num_transactions,
            avg_transaction,
            day_of_week,
            day_of_month,
            month,
            quarter,
            int(is_weekend),
            int(is_month_start),
            int(is_month_end),
            recent_sales,
            int(is_holiday),
            season,
            unique_clients
        ]
    
    def _load_latest_model(self):
        """Carga el modelo más reciente"""
        try:
            latest_model = MLModel.objects.filter(
                model_type='sales_forecast',
                is_active=True
            ).order_by('-created_at').first()
            
            if latest_model:
                model_path = os.path.join(self.model_path, latest_model.model_file)
                if os.path.exists(model_path):
                    self.model = joblib.load(model_path)
                    
                    # Cargar scaler
                    scaler_filename = latest_model.model_file.replace('sales_forecast_', 'scaler_')
                    scaler_path = os.path.join(self.model_path, scaler_filename)
                    if os.path.exists(scaler_path):
                        self.scaler = joblib.load(scaler_path)
                    
                    self.feature_names = latest_model.features_used
                    
        except Exception as e:
            print(f"Error cargando modelo: {e}")


class MLModelService:
    """Servicio general para gestión de modelos ML"""
    
    @staticmethod
    def retrain_model(model_id: str, force: bool = False) -> Dict[str, Any]:
        """Reentrena un modelo específico"""
        try:
            model = MLModel.objects.get(id=model_id)
            
            # Crear log de entrenamiento
            training_log = ModelTrainingLog.objects.create(
                model=model,
                training_type='retrain',
                status='started',
                training_data_size=0
            )
            
            # Ejecutar reentrenamiento
            service = SalesForecastService()
            result = service.train_model()
            
            if result['success']:
                # Actualizar modelo
                model.accuracy = result['r2_score']
                model.r2_score = result['r2_score']
                model.mae = result['mae']
                model.rmse = result['rmse']
                model.last_retrain = timezone.now()
                model.save()
                
                # Actualizar log
                training_log.status = 'completed'
                training_log.accuracy_after = result['r2_score']
                training_log.save()
                
                # Guardar importancia de features
                for i, feature_data in enumerate(result['feature_importance']):
                    FeatureImportance.objects.update_or_create(
                        model=model,
                        feature_name=feature_data['feature'],
                        defaults={
                            'importance_score': feature_data['importance'],
                            'rank': i + 1
                        }
                    )
                
                return {'success': True, 'message': 'Modelo reentrenado exitosamente'}
            else:
                training_log.status = 'failed'
                training_log.error_message = result['error']
                training_log.save()
                
                return {'success': False, 'error': result['error']}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_model_info(model_id: str) -> Dict[str, Any]:
        """Obtiene información de un modelo"""
        try:
            model = MLModel.objects.get(id=model_id)
            
            # Obtener importancia de features
            features = FeatureImportance.objects.filter(model=model).order_by('rank')
            
            return {
                'model': {
                    'id': str(model.id),
                    'name': model.name,
                    'type': model.model_type,
                    'version': model.version,
                    'accuracy': model.accuracy,
                    'r2_score': model.r2_score,
                    'mae': model.mae,
                    'rmse': model.rmse,
                    'training_date': model.training_date,
                    'last_retrain': model.last_retrain,
                    'is_active': model.is_active
                },
                'features': [
                    {
                        'name': f.feature_name,
                        'importance': f.importance_score,
                        'rank': f.rank
                    }
                    for f in features
                ]
            }
            
        except Exception as e:
            return {'error': str(e)}
