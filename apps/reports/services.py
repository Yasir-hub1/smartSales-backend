"""
Servicios para generación dinámica de reportes
"""
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from django.db import connection
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from apps.sales.models import Sale, SaleItem
from apps.products.models import Product
from apps.clients.models import Client


class ReportPromptParser:
    """Parser para interpretar prompts de reportes"""
    
    def __init__(self):
        self.patterns = {
            'ventas': r'(ventas?|sales?)',
            'clientes': r'(clientes?|customers?)',
            'productos': r'(productos?|products?)',
            'fecha': r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|\d{1,2}/\d{1,2}/\d{4})',
            'periodo': r'(del|desde|hasta|al|entre)\s+(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}/\d{1,2}/\d{4})',
            'formato': r'(pdf|excel|pantalla|screen)',
            'agrupacion': r'(agrupado|agrupadas?|por|grouped?)\s+(producto|cliente|fecha|mes|año)',
            'orden': r'(ordenado|ordenadas?|por|order)\s+(nombre|fecha|monto|cantidad)',
            'filtro': r'(top|mejores?|peores?)\s+(\d+)',
            'comparacion': r'(comparar|comparar?|vs|versus)'
        }
    
    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parsea un prompt y extrae los parámetros del reporte"""
        prompt_lower = prompt.lower()
        
        result = {
            'type': 'sales',  # Por defecto
            'date_range': None,
            'format': 'screen',
            'group_by': None,
            'order_by': None,
            'filters': {},
            'limit': None,
            'comparison': False
        }
        
        # Detectar tipo de reporte
        if re.search(self.patterns['clientes'], prompt_lower):
            result['type'] = 'clients'
        elif re.search(self.patterns['productos'], prompt_lower):
            result['type'] = 'products'
        elif re.search(self.patterns['ventas'], prompt_lower):
            result['type'] = 'sales'
        
        # Detectar si se pide "todas" las ventas
        if re.search(r'todas.*ventas|todas.*compras|listar.*ventas|mostrar.*ventas', prompt_lower):
            result['show_all'] = True
            result['limit'] = None  # Sin límite
        
        # Detectar formato
        if re.search(r'pdf', prompt_lower):
            result['format'] = 'pdf'
        elif re.search(r'excel', prompt_lower):
            result['format'] = 'excel'
        
        # Detectar fechas específicas (no rangos) - Formato: "el 18 de octubre"
        specific_date_patterns = [
            # Formato: "el 18 de octubre"
            r'el\s+(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)',
            # Formato: "18 de octubre"
            r'(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?!\s+(hasta|al))',
            # Formato: "del 18 de octubre"
            r'del\s+(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)',
            # Formato: "18/10/2025"
            r'(\d{1,2}/\d{1,2}/\d{4})(?!\s+(al|hasta))'
        ]
        
        # Detectar rango de fechas - Múltiples formatos
        date_range_patterns = [
            # Formato: "desde el 18 de octubre hasta el 19 de octubre"
            r'desde\s+el?\s*(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(hasta|al)\s+el?\s*(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)',
            # Formato: "18 de octubre hasta 19 de octubre"
            r'(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(hasta|al)\s+(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)',
            # Formato: "18/10/2025 al 19/10/2025"
            r'(\d{1,2}/\d{1,2}/\d{4})\s+(al|hasta)\s+(\d{1,2}/\d{1,2}/\d{4})',
            # Formato: "desde 18 de octubre hasta 19 de octubre"
            r'desde\s+(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(hasta|al)\s+(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)',
            # Formato: "18 al 19 de octubre"
            r'(\d{1,2})\s+(al|hasta)\s+(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)',
            # Formato: "del 18 de octubre hasta el 19 de octubre"
            r'del\s+(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(hasta|al)\s+el?\s*(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)'
        ]
        
        date_found = False
        
        # Primero intentar detectar fechas específicas (no rangos)
        for pattern in specific_date_patterns:
            date_match = re.search(pattern, prompt_lower)
            if date_match:
                try:
                    if 'de' in pattern:  # Formato con nombres de meses
                        day, month = date_match.groups()
                        year = timezone.now().year
                        
                        month_names = {
                            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                        }
                        
                        specific_date = datetime(year, month_names[month], int(day)).date()
                        result['specific_date'] = specific_date
                        print(f"Fecha específica detectada: {specific_date}")
                        date_found = True
                        break
                    else:  # Formato con números
                        specific_date = datetime.strptime(date_match.group(1), '%d/%m/%Y').date()
                        result['specific_date'] = specific_date
                        print(f"Fecha específica detectada: {specific_date}")
                        date_found = True
                        break
                except Exception as e:
                    print(f"Error parseando fecha específica: {str(e)}")
                    continue
        
        # Si no se encontró fecha específica, intentar detectar rangos
        if not date_found:
            for pattern in date_range_patterns:
                date_match = re.search(pattern, prompt_lower)
                if date_match:
                    try:
                        if 'de' in pattern:  # Formato con nombres de meses
                            if len(date_match.groups()) == 5:  # "desde X de Y hasta Z de W"
                                day1, month1, _, day2, month2 = date_match.groups()
                                year = timezone.now().year
                            elif len(date_match.groups()) == 4:  # "X de Y hasta Z de W" o "X al Y de Z"
                                if 'al' in date_match.group(0) and 'hasta' not in date_match.group(0):
                                    day1, _, day2, month2 = date_match.groups()
                                    month1 = month2
                                    year = timezone.now().year
                                else:
                                    day1, month1, _, day2, month2 = date_match.groups()
                                    year = timezone.now().year
                            else:  # "X al Y de Z"
                                day1, _, day2, month2 = date_match.groups()
                                month1 = month2
                                year = timezone.now().year
                            
                            month_names = {
                                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                            }
                            
                            start_date = datetime(year, month_names[month1], int(day1)).date()
                            end_date = datetime(year, month_names[month2], int(day2)).date()
                        else:  # Formato con números
                            start_date = datetime.strptime(date_match.group(1), '%d/%m/%Y').date()
                            end_date = datetime.strptime(date_match.group(3), '%d/%m/%Y').date()
                        
                        result['date_range'] = (start_date, end_date)
                        print(f"Rango de fechas detectado: {start_date} a {end_date}")
                        date_found = True
                        break
                    except Exception as e:
                        print(f"Error parseando rango de fechas: {str(e)}")
                        continue
        
        if not date_found:
            month_patterns = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
            }
            
            # PRIMERO: Buscar meses específicos con múltiples patrones
            # Prioridad: meses específicos sobre "mes actual"
            detected_month = None
            detected_month_num = None
            
            # Patrón 1: "de/del/en [mes]" - más común (ej: "ventas de octubre")
            pattern1 = re.search(r'(?:^|\s)(?:de|del|en)\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?:\s|$|de|del)', prompt_lower)
            if pattern1:
                found_month = pattern1.group(1)
                if found_month in month_patterns:
                    detected_month = found_month
                    detected_month_num = month_patterns[found_month]
                    print(f"🔍 Patrón 1 detectado: '{found_month}' en '{prompt}'")
            
            # Patrón 2: "[mes] de/del" - menos común pero posible
            if not detected_month:
                pattern2 = re.search(r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(?:de|del)(?:\s|$)', prompt_lower)
                if pattern2:
                    found_month = pattern2.group(1)
                    if found_month in month_patterns:
                        detected_month = found_month
                        detected_month_num = month_patterns[found_month]
                        print(f"🔍 Patrón 2 detectado: '{found_month}' en '{prompt}'")
            
            # Patrón 3: "[mes]" al final o solo - último recurso
            if not detected_month:
                pattern3 = re.search(r'(?:^|\s)(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?:\s|$)', prompt_lower)
                if pattern3:
                    found_month = pattern3.group(1)
                    # Verificar que no sea parte de "mes actual"
                    if found_month in month_patterns and not re.search(r'mes\s+actual|este\s+mes', prompt_lower):
                        detected_month = found_month
                        detected_month_num = month_patterns[found_month]
                        print(f"🔍 Patrón 3 detectado: '{found_month}' en '{prompt}'")
            
            # Si se detectó un mes específico, usarlo (tiene prioridad)
            if detected_month:
                current_year = timezone.now().year
                start_date = datetime(current_year, detected_month_num, 1).date()
                if detected_month_num == 12:
                    end_date = datetime(current_year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date = datetime(current_year, detected_month_num + 1, 1).date() - timedelta(days=1)
                result['date_range'] = (start_date, end_date)
                print(f"✅ Mes específico detectado: {detected_month} ({detected_month_num}). Rango: {start_date} a {end_date}")
                date_found = True
            
            # SOLO si NO se detectó un mes específico, buscar "mes actual"
            if not date_found:
                # Patrones para "mes actual" - solo si no hay mes específico
                current_month_patterns = [
                    r'(?:^|\s)mes\s+actual(?:\s|$)',
                    r'(?:^|\s)este\s+mes(?:\s|$)',
                    r'(?:^|\s)mes\s+corriente(?:\s|$)',
                    r'(?:^|\s)mes\s+presente(?:\s|$)',
                    r'current\s+month'
                ]
                
                for pattern in current_month_patterns:
                    if re.search(pattern, prompt_lower):
                        now = timezone.now()
                        current_year = now.year
                        current_month = now.month
                        start_date = datetime(current_year, current_month, 1).date()
                        if current_month == 12:
                            end_date = datetime(current_year + 1, 1, 1).date() - timedelta(days=1)
                        else:
                            end_date = datetime(current_year, current_month + 1, 1).date() - timedelta(days=1)
                        result['date_range'] = (start_date, end_date)
                        print(f"✅ Mes actual detectado ({current_month}). Rango: {start_date} a {end_date}")
                        date_found = True
                        break
        
        # Log si no se detectó ninguna fecha
        if not date_found:
            print(f"⚠️ No se detectó ninguna fecha en el prompt: '{prompt}'")
            print(f"   Se mostrarán TODAS las ventas (sin filtro de fecha)")
        
        # Detectar agrupación SOLO si se especifica explícitamente
        if re.search(r'agrupado.*producto|agrupa.*producto|por producto', prompt_lower):
            result['group_by'] = 'product'
        elif re.search(r'agrupado.*cliente|agrupa.*cliente|por cliente', prompt_lower):
            result['group_by'] = 'client'
        elif re.search(r'agrupado.*fecha|agrupa.*fecha|por fecha', prompt_lower):
            result['group_by'] = 'date'
        # Si no se especifica agrupación, NO agrupar por defecto
        
        # Detectar ordenamiento
        if re.search(r'ordenado.*nombre', prompt_lower):
            result['order_by'] = 'name'
        elif re.search(r'ordenado.*fecha', prompt_lower):
            result['order_by'] = 'date'
        elif re.search(r'ordenado.*monto', prompt_lower):
            result['order_by'] = 'amount'
        
        # Detectar límite (top N)
        limit_match = re.search(r'top\s+(\d+)', prompt_lower)
        if limit_match:
            result['limit'] = int(limit_match.group(1))
        
        # Detectar comparación
        if re.search(self.patterns['comparacion'], prompt_lower):
            result['comparison'] = True
        
        return result
    

class DynamicReportGenerator:
    """Generador dinámico de reportes"""
    
    def __init__(self):
        self.parser = ReportPromptParser()
    
    def generate_report(self, prompt: str, format_type: str = 'screen') -> Dict[str, Any]:
        """Genera un reporte basado en el prompt"""
        parsed_params = self.parser.parse_prompt(prompt)
        parsed_params['format'] = format_type
        
        if parsed_params['type'] == 'sales':
            return self._generate_sales_report(parsed_params)
        elif parsed_params['type'] == 'clients':
            return self._generate_clients_report(parsed_params)
        elif parsed_params['type'] == 'products':
            return self._generate_products_report(parsed_params)
        else:
            return self._generate_sales_report(parsed_params)
    
    def _generate_sales_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte de ventas"""
        print(f"Generando reporte de ventas con parámetros: {params}")
        
        queryset = Sale.objects.select_related('client', 'user').prefetch_related('items__product')
        print(f"Queryset inicial: {queryset.count()} ventas")
        
        # Aplicar filtros de fecha
        if params.get('specific_date'):
            specific_date = params['specific_date']
            print(f"Aplicando filtro de fecha específica: {specific_date}")
            # Usar filtro de rango para un día específico con timezone
            from datetime import timedelta
            
            start_datetime = timezone.make_aware(datetime.combine(specific_date, datetime.min.time()))
            end_datetime = start_datetime + timedelta(days=1)
            
            print(f"Rango de filtro: {start_datetime} a {end_datetime}")
            
            queryset = queryset.filter(
                created_at__gte=start_datetime,
                created_at__lt=end_datetime
            )
            print(f"Después de filtro de fecha específica: {queryset.count()} ventas")
            
            # Verificar que el filtro se aplicó correctamente
            if queryset.count() == 0:
                print("⚠️ No se encontraron ventas en la fecha especificada")
            else:
                print(f"✅ Filtro aplicado correctamente: {queryset.count()} ventas encontradas")
        elif params.get('date_range'):
            start_date, end_date = params['date_range']
            print(f"📅 Aplicando filtro de rango de fechas: {start_date} a {end_date}")
            print(f"   Tipo start_date: {type(start_date)}, Tipo end_date: {type(end_date)}")
            
            # Convertir fechas a datetime con timezone para filtrado correcto
            # start_date debe ser el inicio del primer día del mes
            start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            
            # end_date debe ser el inicio del primer día del mes siguiente (exclusivo)
            # end_date ya es el último día del mes, así que sumamos 1 día para obtener el inicio del mes siguiente
            if end_date.month == 12:
                next_month_start = datetime(end_date.year + 1, 1, 1, 0, 0, 0)
            else:
                next_month_start = datetime(end_date.year, end_date.month + 1, 1, 0, 0, 0)
            
            end_datetime = timezone.make_aware(next_month_start)
            
            print(f"🔍 Rango de filtro (datetime):")
            print(f"   Desde: {start_datetime} (inclusive)")
            print(f"   Hasta: {end_datetime} (exclusivo)")
            print(f"   Esto filtra desde {start_date} hasta {end_date} inclusive")
            
            # Obtener algunas ventas de ejemplo antes del filtro para debugging
            sample_before = queryset.order_by('-created_at')[:5]
            print(f"📊 Ejemplo de ventas antes del filtro (últimas 5):")
            for sale in sample_before:
                print(f"   - {sale.created_at.date()} ({sale.created_at}) - Total: {sale.total}")
            
            queryset = queryset.filter(
                created_at__gte=start_datetime,
                created_at__lt=end_datetime
            )
            
            count_after = queryset.count()
            print(f"📊 Después de filtro de rango de fechas: {count_after} ventas")
            
            # Mostrar algunas ventas después del filtro para verificar
            if count_after > 0:
                sample_after = queryset.order_by('-created_at')[:5]
                print(f"📊 Ejemplo de ventas después del filtro (últimas 5):")
                for sale in sample_after:
                    print(f"   - {sale.created_at.date()} ({sale.created_at}) - Total: {sale.total}")
            
            # Verificar que el filtro se aplicó correctamente
            if count_after == 0:
                print("⚠️ No se encontraron ventas en el rango de fechas especificado")
                print(f"   Verificando si hay ventas en la base de datos...")
                all_sales = Sale.objects.all()
                print(f"   Total de ventas en BD: {all_sales.count()}")
                if all_sales.exists():
                    first_sale = all_sales.order_by('created_at').first()
                    last_sale = all_sales.order_by('-created_at').first()
                    print(f"   Primera venta: {first_sale.created_at.date()} ({first_sale.created_at})")
                    print(f"   Última venta: {last_sale.created_at.date()} ({last_sale.created_at})")
            else:
                print(f"✅ Filtro aplicado correctamente: {count_after} ventas encontradas")
        
        # SOLO agrupar si se especifica explícitamente en el prompt
        if params.get('group_by') == 'product':
            print("Agrupando por producto")
            return self._group_sales_by_product(queryset, params)
        elif params.get('group_by') == 'client':
            print("Agrupando por cliente")
            return self._group_sales_by_client(queryset, params)
        else:
            print("Listando TODAS las ventas sin agrupar")
            return self._get_sales_list(queryset, params)
    
    def _group_sales_by_product(self, queryset, params: Dict[str, Any]) -> List[Dict]:
        """Agrupa ventas por producto usando el queryset filtrado"""
        from django.db.models import Sum, Count, F
        
        # Obtener los IDs de las ventas del queryset filtrado
        sale_ids = list(queryset.values_list('id', flat=True))
        
        if not sale_ids:
            return []
        
        # Agrupar por producto usando los IDs filtrados
        from apps.sales.models import SaleItem
        results = SaleItem.objects.filter(
            sale_id__in=sale_ids
        ).values(
            'product__name', 'product__sku'
        ).annotate(
            cantidad_vendida=Sum('quantity'),
            total_vendido=Sum(F('quantity') * F('price')),
            numero_ventas=Count('sale_id', distinct=True)
        ).order_by('-total_vendido')
        
        # Convertir a formato de diccionario
        formatted_results = []
        for item in results:
            formatted_results.append({
                'producto': item['product__name'],
                'sku': item['product__sku'],
                'cantidad_vendida': item['cantidad_vendida'],
                'total_vendido': float(item['total_vendido'] or 0),
                'numero_ventas': item['numero_ventas']
            })
        
        if params.get('limit'):
            formatted_results = formatted_results[:params['limit']]
        
        return formatted_results
    
    def _group_sales_by_client(self, queryset, params: Dict[str, Any]) -> List[Dict]:
        """Agrupa ventas por cliente usando el queryset filtrado"""
        from django.db.models import Sum, Count, Min, Max
        
        # Agrupar por cliente usando el queryset filtrado
        results = queryset.values(
            'client__name', 'client__email'
        ).annotate(
            numero_compras=Count('id'),
            monto_total=Sum('total'),
            primera_compra=Min('created_at'),
            ultima_compra=Max('created_at')
        ).order_by('-monto_total')
        
        # Convertir a formato de diccionario
        formatted_results = []
        for item in results:
            formatted_results.append({
                'cliente': item['client__name'] or 'Anónimo',
                'email': item['client__email'] or '',
                'numero_compras': item['numero_compras'],
                'monto_total': float(item['monto_total']),
                'primera_compra': item['primera_compra'].strftime('%d/%m/%Y') if item['primera_compra'] else 'N/A',
                'ultima_compra': item['ultima_compra'].strftime('%d/%m/%Y') if item['ultima_compra'] else 'N/A'
            })
        
        if params.get('limit'):
            formatted_results = formatted_results[:params['limit']]
        
        return formatted_results
    
    def _get_sales_list(self, queryset, params: Dict[str, Any]) -> List[Dict]:
        """Obtiene lista de ventas"""
        try:
            print(f"Procesando {queryset.count()} ventas...")
            sales_data = []
            
            # Ordenar por fecha más reciente primero
            queryset = queryset.order_by('-created_at')
            
            for sale in queryset:
                # Obtener productos de la venta
                products = []
                for item in sale.items.all():
                    products.append(f"{item.product.name} (x{item.quantity})")
                
                sales_data.append({
                    'id': str(sale.id),
                    'cliente': sale.client.name if sale.client else 'Anónimo',
                    'fecha': sale.created_at.strftime('%d/%m/%Y %H:%M'),
                    'total': float(sale.total),
                    'estado': sale.status,
                    'metodo_pago': sale.payment_status,
                    'productos': products
                })
            
            print(f"Procesadas {len(sales_data)} ventas")
            
            # Solo aplicar límite si se especifica explícitamente Y no se pide "todas"
            if params.get('limit') and not params.get('show_all'):
                sales_data = sales_data[:params['limit']]
                print(f"Limitadas a {len(sales_data)} ventas")
            elif params.get('show_all'):
                print(f"Mostrando TODAS las {len(sales_data)} ventas")
            
            return sales_data
        except Exception as e:
            print(f"Error obteniendo lista de ventas: {str(e)}")
            return [{"error": f"Error obteniendo ventas: {str(e)}"}]
    
    def _generate_clients_report(self, params: Dict[str, Any]) -> List[Dict]:
        """Genera reporte de clientes"""
        try:
            queryset = Client.objects.all()
            
            clients_data = []
            for client in queryset:
                # Obtener ventas del cliente usando la relación inversa correcta
                client_sales = Sale.objects.filter(client=client)
                
                # Aplicar filtros de fecha si existen
                if params.get('date_range'):
                    start_date, end_date = params['date_range']
                    client_sales = client_sales.filter(created_at__date__range=[start_date, end_date])
                
                total_purchases = client_sales.count()
                total_amount = sum(sale.total for sale in client_sales)
                
                clients_data.append({
                    'nombre': client.name,
                    'email': client.email,
                    'telefono': client.phone,
                    'total_compras': total_purchases,
                    'monto_total': float(total_amount),
                    'ultima_compra': client.last_purchase_date.strftime('%d/%m/%Y') if client.last_purchase_date else 'Nunca'
                })
            
            if params.get('limit'):
                clients_data = clients_data[:params['limit']]
            
            return clients_data
        except Exception as e:
            print(f"Error generando reporte de clientes: {str(e)}")
            return [{"error": f"Error generando reporte de clientes: {str(e)}"}]
    
    def _generate_products_report(self, params: Dict[str, Any]) -> List[Dict]:
        """Genera reporte de productos"""
        queryset = Product.objects.filter(is_active=True)
        
        products_data = []
        for product in queryset:
            # Obtener estadísticas de ventas
            sales_stats = SaleItem.objects.filter(
                product=product,
                sale__created_at__date__range=params['date_range'] if params['date_range'] else [None, None]
            ).aggregate(
                total_sold=Sum('quantity'),
                total_revenue=Sum('quantity') * Sum('price')
            )
            
            products_data.append({
                'nombre': product.name,
                'sku': product.sku,
                'precio': float(product.price),
                'stock': product.stock,
                'categoria': product.category.name if product.category else 'Sin categoría',
                'unidades_vendidas': sales_stats['total_sold'] or 0,
                'ingresos': float(sales_stats['total_revenue'] or 0)
            })
        
        if params['limit']:
            products_data = products_data[:params['limit']]
        
        return products_data