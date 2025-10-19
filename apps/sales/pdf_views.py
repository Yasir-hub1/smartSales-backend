"""
Views para manejo de PDFs de notas de venta
"""
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Sale, SaleReceipt
import os


@api_view(['GET'])
@permission_classes([AllowAny])
def download_sale_receipt(request, sale_id):
    """Descargar PDF de nota de venta"""
    try:
        sale = get_object_or_404(Sale, id=sale_id)
        
        # Obtener o crear comprobante
        receipt, created = SaleReceipt.objects.get_or_create(
            sale=sale,
            defaults={'receipt_number': f"NV-{sale.id.hex[:8].upper()}"}
        )
        
        # Si no tiene PDF o se solicita regenerar
        if not receipt.pdf_file or request.GET.get('regenerate') == 'true':
            pdf_url = receipt.generate_pdf()
        else:
            pdf_url = receipt.pdf_file.url
        
        # Leer archivo PDF
        if receipt.pdf_file and os.path.exists(receipt.pdf_file.path):
            with open(receipt.pdf_file.path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="nota_venta_{sale.id.hex[:8]}.pdf"'
                return response
        else:
            return Response({
                'error': 'PDF no disponible'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sale_receipt_info(request, sale_id):
    """Obtener información del comprobante de venta"""
    try:
        sale = get_object_or_404(Sale, id=sale_id)
        
        # Obtener o crear comprobante
        receipt, created = SaleReceipt.objects.get_or_create(
            sale=sale,
            defaults={'receipt_number': f"NV-{sale.id.hex[:8].upper()}"}
        )
        
        return Response({
            'sale_id': str(sale.id),
            'receipt_number': receipt.receipt_number,
            'pdf_url': receipt.pdf_file.url if receipt.pdf_file else None,
            'created_at': sale.created_at.isoformat(),
            'total': float(sale.total),
            'status': sale.status,
            'payment_status': sale.payment_status
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
