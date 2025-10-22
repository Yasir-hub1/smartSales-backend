from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from .models import MLModel, Prediction
from .serializers import MLModelSerializer, PredictionSerializer
from .services import SalesForecastService, MLModelService
import json


class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.filter(is_active=True)
    serializer_class = MLModelSerializer

    @action(detail=False, methods=['post'])
    def train_sales_forecast(self, request):
        """Entrenar modelo de pronóstico de ventas"""
        try:
            service = SalesForecastService()
            use_synthetic = request.data.get('use_synthetic', True)
            
            result = service.train_model(use_synthetic=use_synthetic)
            
            if result['success']:
                return Response({
                    'success': True,
                    'message': 'Modelo entrenado exitosamente',
                    'metrics': {
                        'r2_score': result['r2_score'],
                        'mae': result['mae'],
                        'rmse': result['rmse'],
                        'cv_mean': result['cv_mean'],
                        'cv_std': result['cv_std']
                    },
                    'feature_importance': result['feature_importance']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def retrain(self, request, pk=None):
        """Reentrenar modelo específico"""
        try:
            result = MLModelService.retrain_model(pk, force=True)
            return Response(result)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def info(self, request, pk=None):
        """Obtener información detallada del modelo"""
        try:
            result = MLModelService.get_model_info(pk)
            return Response(result)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.filter(is_active=True)
    serializer_class = PredictionSerializer

    @action(detail=False, methods=['post'])
    def forecast_sales(self, request):
        """Generar pronóstico de ventas"""
        try:
            days_ahead = request.data.get('days_ahead', 30)
            service = SalesForecastService()
            
            predictions = service.predict_sales(days_ahead=days_ahead)
            
            return Response({
                'success': True,
                'predictions': predictions,
                'total_days': len(predictions),
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def historical_data(self, request):
        """Obtener datos históricos para el dashboard"""
        try:
            from apps.sales.models import Sale, SaleItem
            from apps.products.models import Product
            from django.db.models import Sum, Count, Avg
            from datetime import timedelta
            
            # Parámetros de filtro
            days_back = int(request.query_params.get('days_back', 365))
            group_by = request.query_params.get('group_by', 'day')  # day, week, month
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Obtener datos de ventas
            sales_data = Sale.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                is_active=True
            ).select_related('client').prefetch_related('items__product')
            
            # Agrupar datos según el parámetro
            if group_by == 'day':
                historical_data = []
                current_date = start_date.date()
                
                while current_date <= end_date.date():
                    day_sales = sales_data.filter(created_at__date=current_date)
                    total_sales = sum(sale.total for sale in day_sales)
                    num_transactions = day_sales.count()
                    
                    historical_data.append({
                        'date': current_date.isoformat(),
                        'total_sales': float(total_sales),
                        'num_transactions': num_transactions,
                        'avg_transaction': float(total_sales / num_transactions) if num_transactions > 0 else 0
                    })
                    
                    current_date += timedelta(days=1)
                    
            elif group_by == 'week':
                # Agrupar por semana
                historical_data = []
                current_date = start_date.date()
                
                while current_date <= end_date.date():
                    week_end = current_date + timedelta(days=6)
                    week_sales = sales_data.filter(
                        created_at__date__gte=current_date,
                        created_at__date__lte=week_end
                    )
                    total_sales = sum(sale.total for sale in week_sales)
                    num_transactions = week_sales.count()
                    
                    historical_data.append({
                        'date': current_date.isoformat(),
                        'total_sales': float(total_sales),
                        'num_transactions': num_transactions,
                        'avg_transaction': float(total_sales / num_transactions) if num_transactions > 0 else 0
                    })
                    
                    current_date += timedelta(days=7)
                    
            elif group_by == 'month':
                # Agrupar por mes
                historical_data = []
                current_date = start_date.replace(day=1).date()
                
                while current_date <= end_date.date():
                    if current_date.month == 12:
                        next_month = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        next_month = current_date.replace(month=current_date.month + 1)
                    
                    month_sales = sales_data.filter(
                        created_at__date__gte=current_date,
                        created_at__date__lt=next_month
                    )
                    total_sales = sum(sale.total for sale in month_sales)
                    num_transactions = month_sales.count()
                    
                    historical_data.append({
                        'date': current_date.isoformat(),
                        'total_sales': float(total_sales),
                        'num_transactions': num_transactions,
                        'avg_transaction': float(total_sales / num_transactions) if num_transactions > 0 else 0
                    })
                    
                    current_date = next_month
            
            return Response({
                'success': True,
                'data': historical_data,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days_back': days_back,
                    'group_by': group_by
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def product_analysis(self, request):
        """Análisis de productos más vendidos"""
        try:
            from apps.sales.models import SaleItem
            from django.db.models import Sum, Count
            
            days_back = int(request.query_params.get('days_back', 90))
            limit = int(request.query_params.get('limit', 10))
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Obtener productos más vendidos
            product_stats = SaleItem.objects.filter(
                sale__created_at__gte=start_date,
                sale__created_at__lte=end_date,
                sale__is_active=True
            ).values(
                'product__name',
                'product__sku',
                'product__category__name'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum('quantity') * Sum('price'),
                num_sales=Count('sale')
            ).order_by('-total_revenue')[:limit]
            
            return Response({
                'success': True,
                'data': list(product_stats),
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days_back': days_back
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def client_analysis(self, request):
        """Análisis de clientes"""
        try:
            from apps.sales.models import Sale
            from django.db.models import Sum, Count, Avg
            
            days_back = int(request.query_params.get('days_back', 90))
            limit = int(request.query_params.get('limit', 10))
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Obtener clientes con más compras
            client_stats = Sale.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                is_active=True
            ).values(
                'client__name',
                'client__email'
            ).annotate(
                total_purchases=Count('id'),
                total_spent=Sum('total'),
                avg_purchase=Avg('total')
            ).order_by('-total_spent')[:limit]
            
            return Response({
                'success': True,
                'data': list(client_stats),
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days_back': days_back
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
