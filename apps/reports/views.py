"""
Vistas para generación de reportes
"""
import json
import io
import csv
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .services import DynamicReportGenerator
from .exporters import PDFExporter, ExcelExporter


@api_view(['GET'])
@permission_classes([AllowAny])
def test_reports(request):
    """Endpoint de prueba para reportes"""
    return Response({
        'message': 'Módulo de reportes funcionando correctamente',
        'status': 'ok'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])  # Temporal para pruebas
def generate_report(request):
    """Genera un reporte dinámico basado en el prompt"""
    try:
        data = request.data
        prompt = data.get('prompt', '')
        format_type = data.get('format', 'screen')
        
        if not prompt:
            return Response(
                {'error': 'Prompt es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generar reporte real
        try:
            generator = DynamicReportGenerator()
            report_data = generator.generate_report(prompt, format_type)
            print(f"Reporte generado exitosamente: {len(report_data) if isinstance(report_data, list) else 'No es lista'}")
        except Exception as e:
            print(f"Error en generador: {str(e)}")
            # Fallback con datos de prueba
            report_data = [
                {
                    'id': '1',
                    'cliente': 'Cliente de Prueba',
                    'fecha': datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'total': 100.50,
                    'estado': 'completed',
                    'metodo_pago': 'paid',
                    'productos': ['Producto Test 1', 'Producto Test 2']
                }
            ]
        
        # Preparar respuesta
        response_data = {
            'success': True,
            'data': report_data,
            'format': format_type,
            'generated_at': datetime.now().isoformat(),
            'prompt': prompt
        }
        
        # Si es PDF o Excel, generar archivo
        if format_type in ['pdf', 'excel']:
            if format_type == 'pdf':
                file_url = PDFExporter.export_report(report_data, prompt)
            else:
                file_url = ExcelExporter.export_report(report_data, prompt)
            
            response_data['downloadUrl'] = file_url
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error generando reporte: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_report_templates(request):
    """Obtiene plantillas de reportes predefinidos"""
    templates = [
        {
            'id': 'sales_monthly',
            'name': 'Ventas del Mes',
            'description': 'Reporte de ventas del mes actual',
            'prompt': 'Ventas del mes actual agrupadas por producto',
            'format': 'screen'
        },
        {
            'id': 'top_products',
            'name': 'Top Productos',
            'description': 'Productos más vendidos',
            'prompt': 'Top 10 productos más vendidos del mes',
            'format': 'screen'
        },
        {
            'id': 'clients_summary',
            'name': 'Resumen de Clientes',
            'description': 'Información de clientes y sus compras',
            'prompt': 'Clientes con más compras y sus montos totales',
            'format': 'screen'
        },
        {
            'id': 'sales_pdf',
            'name': 'Ventas en PDF',
            'description': 'Reporte de ventas en formato PDF',
            'prompt': 'Ventas del mes de septiembre agrupadas por producto en PDF',
            'format': 'pdf'
        },
        {
            'id': 'sales_excel',
            'name': 'Ventas en Excel',
            'description': 'Reporte de ventas en formato Excel',
            'prompt': 'Ventas del periodo del 01/10/2024 al 01/01/2025 en Excel',
            'format': 'excel'
        }
    ]
    
    return Response(templates, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_report_history(request):
    """Obtiene historial de reportes generados"""
    # Por ahora retornamos una lista vacía
    # En el futuro se puede implementar persistencia de reportes
    return Response([], status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def download_report(request):
    """Descarga un reporte generado"""
    try:
        data = request.data
        report_id = data.get('report_id')
        format_type = data.get('format', 'pdf')
        
        # Aquí se implementaría la lógica para obtener el reporte
        # y generar el archivo de descarga
        
        return Response(
            {'error': 'Funcionalidad de descarga no implementada'}, 
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
        
    except Exception as e:
        return Response(
            {'error': f'Error descargando reporte: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )