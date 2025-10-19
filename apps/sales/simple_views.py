"""
Views simples para obtener datos de ventas
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Sale, SaleItem


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sale_data(request, sale_id):
    """Obtener datos completos de una venta para generar PDF"""
    try:
        sale = get_object_or_404(Sale, id=sale_id)
        
        # Obtener items de la venta
        items = []
        for item in sale.items.all():
            items.append({
                'id': str(item.id),
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': float(item.price),
                'subtotal': float(item.subtotal)
            })
        
        # Datos del cliente
        client_data = {
            'name': sale.client.name if sale.client else 'Cliente Anónimo',
            'email': sale.client.email if sale.client else 'anonimo@tienda.com',
            'phone': sale.client.phone if sale.client else '000-000-0000'
        }
        
        # Datos de la venta
        sale_data = {
            'id': str(sale.id),
            'subtotal': float(sale.subtotal),
            'discount': float(sale.discount),
            'total': float(sale.total),
            'status': sale.status,
            'payment_status': sale.payment_status,
            'total_items': sale.total_items,
            'notes': sale.notes,
            'created_at': sale.created_at.isoformat(),
            'client': client_data,
            'items': items
        }
        
        return Response({
            'success': True,
            'sale': sale_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
