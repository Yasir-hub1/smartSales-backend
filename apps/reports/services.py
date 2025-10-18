"""
Servicios para generación de reportes dinámicos
"""
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from apps.sales.models import Sale, SaleItem
from apps.products.models import Product, Category
from apps.clients.models import Client


class ReportPromptParser:
    """Parser inteligente de prompts para reportes"""
    
    def __init__(self):
        self.date_patterns = {
            'del (\d{1,2})/(\d{1,2})/(\d{4}) al (\d{1,2})/(\d{1,2})/(\d{4})': self._parse_date_range,
            'mes de (\w+)': self._parse_month,
            'último trimestre': self._parse_last_quarter,
            'últimos (\d+) días': self._parse_last_days,
            'este año': self._parse_this_year,
            'año pasado': self._parse_last_year,
        }
        
        self.report_types = {
            'ventas': 'sales',
            'productos': 'products',
            'clientes': 'clients',
            'financiero': 'financial',
            'inventario': 'inventory',
            'predicciones': 'predictions'
        }
        
        self.formats = {
            'pdf': 'pdf',
            'excel': 'excel',
            'pantalla': 'json',
            'json': 'json',
            'csv': 'csv'
        }
        
        self.grouping_options = {
            'por producto': 'product',
            'por cliente': 'client',
            'por categoría': 'category',
            'por fecha': 'date',
            'por mes': 'month',
            'por día': 'day'
        }
    
    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parsea un prompt y extrae los parámetros"""
        prompt_lower = prompt.lower()
        
        result = {
            'report_type': 'sales',
            'format': 'pdf',
            'date_range': self._get_default_date_range(),
            'grouping': None,
            'filters': {},
            'fields': [],
            'aggregations': []
        }
        
        # Detectar tipo de reporte
        for keyword, report_type in self.report_types.items():
            if keyword in prompt_lower:
                result['report_type'] = report_type
                break
        
        # Detectar formato
        for keyword, format_type in self.formats.items():
            if keyword in prompt_lower:
                result['format'] = format_type
                break
        
        # Detectar rango de fechas
        for pattern, parser_func in self.date_patterns.items():
            match = re.search(pattern, prompt_lower)
            if match:
                result['date_range'] = parser_func(match)
                break
        
        # Detectar agrupamiento
        for keyword, grouping in self.grouping_options.items():
            if keyword in prompt_lower:
                result['grouping'] = grouping
                break
        
        # Detectar campos específicos
        if 'nombre del cliente' in prompt_lower:
            result['fields'].append('client_name')
        if 'cantidad de compras' in prompt_lower:
            result['fields'].append('purchase_count')
        if 'monto total' in prompt_lower:
            result['fields'].append('total_amount')
        if 'rango de fechas' in prompt_lower:
            result['fields'].append('date_range')
        
        # Detectar filtros
        if 'clientes específicos' in prompt_lower:
            result['filters']['specific_clients'] = True
        if 'rangos de montos' in prompt_lower:
            result['filters']['amount_range'] = True
        if 'categorías' in prompt_lower:
            result['filters']['categories'] = True
        
        return result
    
    def _parse_date_range(self, match) -> Dict[str, datetime]:
        """Parsea rango de fechas del formato dd/mm/yyyy al dd/mm/yyyy"""
        day1, month1, year1, day2, month2, year2 = match.groups()
        start_date = datetime(int(year1), int(month1), int(day1))
        end_date = datetime(int(year2), int(month2), int(day2))
        return {'start': start_date, 'end': end_date}
    
    def _parse_month(self, match) -> Dict[str, datetime]:
        """Parsea mes específico"""
        month_name = match.group(1)
        month_map = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        month_num = month_map.get(month_name.lower(), 1)
        year = timezone.now().year
        start_date = datetime(year, month_num, 1)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
        return {'start': start_date, 'end': end_date}
    
    def _parse_last_quarter(self, match) -> Dict[str, datetime]:
        """Parsea último trimestre"""
        now = timezone.now()
        current_quarter = (now.month - 1) // 3 + 1
        start_month = (current_quarter - 1) * 3 + 1
        start_date = datetime(now.year, start_month, 1)
        if start_month == 10:
            end_date = datetime(now.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(now.year, start_month + 3, 1) - timedelta(days=1)
        return {'start': start_date, 'end': end_date}
    
    def _parse_last_days(self, match) -> Dict[str, datetime]:
        """Parsea últimos N días"""
        days = int(match.group(1))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        return {'start': start_date, 'end': end_date}
    
    def _parse_this_year(self, match) -> Dict[str, datetime]:
        """Parsea este año"""
        year = timezone.now().year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        return {'start': start_date, 'end': end_date}
    
    def _parse_last_year(self, match) -> Dict[str, datetime]:
        """Parsea año pasado"""
        year = timezone.now().year - 1
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        return {'start': start_date, 'end': end_date}
    
    def _get_default_date_range(self) -> Dict[str, datetime]:
        """Rango de fechas por defecto (último mes)"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        return {'start': start_date, 'end': end_date}


class ReportGenerator:
    """Generador dinámico de reportes"""
    
    def __init__(self, parameters: Dict[str, Any]):
        self.parameters = parameters
        self.data = None
    
    def generate_sales_report(self) -> Dict[str, Any]:
        """Genera reporte de ventas"""
        queryset = Sale.objects.filter(is_active=True)
        
        # Aplicar filtros de fecha
        date_range = self.parameters.get('date_range', {})
        if date_range:
            queryset = queryset.filter(
                created_at__date__gte=date_range['start'].date(),
                created_at__date__lte=date_range['end'].date()
            )
        
        # Aplicar agrupamiento
        grouping = self.parameters.get('grouping')
        if grouping == 'product':
            queryset = queryset.prefetch_related('items__product')
            data = self._group_by_product(queryset)
        elif grouping == 'client':
            queryset = queryset.select_related('client')
            data = self._group_by_client(queryset)
        elif grouping == 'date':
            data = self._group_by_date(queryset)
        elif grouping == 'month':
            data = self._group_by_month(queryset)
        else:
            data = self._get_sales_summary(queryset)
        
        return {
            'type': 'sales',
            'data': data,
            'parameters': self.parameters,
            'generated_at': timezone.now()
        }
    
    def generate_products_report(self) -> Dict[str, Any]:
        """Genera reporte de productos"""
        queryset = Product.objects.filter(is_active=True)
        
        # Aplicar filtros
        if self.parameters.get('filters', {}).get('categories'):
            queryset = queryset.select_related('category')
        
        # Agregar estadísticas de ventas
        queryset = queryset.annotate(
            total_sold=Sum('saleitem__quantity', default=0),
            total_revenue=Sum('saleitem__subtotal', default=0)
        )
        
        data = list(queryset.values(
            'id', 'name', 'sku', 'price', 'stock', 'category__name',
            'total_sold', 'total_revenue'
        ))
        
        return {
            'type': 'products',
            'data': data,
            'parameters': self.parameters,
            'generated_at': timezone.now()
        }
    
    def generate_clients_report(self) -> Dict[str, Any]:
        """Genera reporte de clientes"""
        queryset = Client.objects.filter(is_active=True)
        
        # Agregar estadísticas de compras
        queryset = queryset.annotate(
            total_purchases=Sum('sale__total', default=0),
            purchase_count=Count('sale', default=0)
        )
        
        data = list(queryset.values(
            'id', 'name', 'email', 'segment', 'total_purchases', 'purchase_count'
        ))
        
        return {
            'type': 'clients',
            'data': data,
            'parameters': self.parameters,
            'generated_at': timezone.now()
        }
    
    def _group_by_product(self, queryset):
        """Agrupa ventas por producto"""
        from django.db.models import Sum, Count
        
        items = SaleItem.objects.filter(
            sale__in=queryset
        ).select_related('product').values(
            'product__name', 'product__sku'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal'),
            sale_count=Count('sale')
        )
        
        return list(items)
    
    def _group_by_client(self, queryset):
        """Agrupa ventas por cliente"""
        return list(queryset.values(
            'client__name', 'client__email'
        ).annotate(
            total_amount=Sum('total'),
            sale_count=Count('id')
        ))
    
    def _group_by_date(self, queryset):
        """Agrupa ventas por fecha"""
        return list(queryset.extra(
            select={'sale_date': 'date(created_at)'}
        ).values('sale_date').annotate(
            total_amount=Sum('total'),
            sale_count=Count('id')
        ).order_by('sale_date'))
    
    def _group_by_month(self, queryset):
        """Agrupa ventas por mes"""
        return list(queryset.extra(
            select={'sale_month': 'strftime("%Y-%m", created_at)'}
        ).values('sale_month').annotate(
            total_amount=Sum('total'),
            sale_count=Count('id')
        ).order_by('sale_month'))
    
    def _get_sales_summary(self, queryset):
        """Obtiene resumen de ventas"""
        summary = queryset.aggregate(
            total_sales=Sum('total'),
            sale_count=Count('id'),
            average_sale=Avg('total')
        )
        
        return {
            'summary': summary,
            'recent_sales': list(queryset.order_by('-created_at')[:10].values(
                'id', 'client__name', 'total', 'created_at'
            ))
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Genera el reporte según el tipo"""
        report_type = self.parameters.get('report_type', 'sales')
        
        if report_type == 'sales':
            return self.generate_sales_report()
        elif report_type == 'products':
            return self.generate_products_report()
        elif report_type == 'clients':
            return self.generate_clients_report()
        else:
            return {'error': 'Tipo de reporte no soportado'}
