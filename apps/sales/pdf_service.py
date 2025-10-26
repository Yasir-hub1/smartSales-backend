"""
Servicio para generar notas de venta en PDF
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
import os
import uuid


class SaleReceiptPDFService:
    """Servicio para generar PDF de notas de venta"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Estilo para el título
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=colors.darkgreen
        ))
        
        # Estilo para información de la empresa
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            textColor=colors.grey
        ))
    
    def generate_sale_receipt(self, sale):
        """Generar PDF de nota de venta"""
        # Crear nombre único para el archivo
        filename = f"nota_venta_{sale.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Crear directorio si no existe
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'receipts')
        os.makedirs(pdf_dir, exist_ok=True)
        
        filepath = os.path.join(pdf_dir, filename)
        
        # Crear documento PDF
        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Contenido del PDF
        story = []
        
        # Encabezado
        story.extend(self._create_header(sale))
        
        # Información de la empresa
        story.extend(self._create_company_info())
        
        # Información del cliente
        story.extend(self._create_client_info(sale))
        
        # Detalles de la venta
        story.extend(self._create_sale_details(sale))
        
        # Tabla de productos
        story.extend(self._create_products_table(sale))
        
        # Totales
        story.extend(self._create_totals(sale))
        
        # Pie de página
        story.extend(self._create_footer())
        
        # Construir PDF
        doc.build(story)
        
        return filepath, filename
    
    def _create_header(self, sale):
        """Crear encabezado del PDF"""
        elements = []
        
        # Título
        elements.append(Paragraph("NOTA DE VENTA", self.styles['CustomTitle']))
        
        # Número de venta
        elements.append(Paragraph(f"<b>Número de Venta:</b> {sale.id}", self.styles['Normal']))
        
        # Fecha
        elements.append(Paragraph(f"<b>Fecha:</b> {sale.created_at.strftime('%d/%m/%Y %H:%M')}", self.styles['Normal']))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_company_info(self):
        """Crear información de la empresa"""
        elements = []
        
        elements.append(Paragraph("SmartSales365", self.styles['CustomSubtitle']))
        elements.append(Paragraph("Sistema de Gestión de Ventas", self.styles['CompanyInfo']))
        elements.append(Paragraph("Email: info@SmartSales365.com", self.styles['CompanyInfo']))
        elements.append(Paragraph("Teléfono: +52 55 1234 5678", self.styles['CompanyInfo']))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_client_info(self, sale):
        """Crear información del cliente"""
        elements = []
        
        elements.append(Paragraph("INFORMACIÓN DEL CLIENTE", self.styles['CustomSubtitle']))
        
        client_info = [
            f"<b>Nombre:</b> {sale.client.name}",
            f"<b>Email:</b> {sale.client.email}",
            f"<b>Teléfono:</b> {sale.client.phone}"
        ]
        
        for info in client_info:
            elements.append(Paragraph(info, self.styles['Normal']))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_sale_details(self, sale):
        """Crear detalles de la venta"""
        elements = []
        
        elements.append(Paragraph("DETALLES DE LA VENTA", self.styles['CustomSubtitle']))
        
        # Estado de la venta
        status_map = {
            'pending': 'Pendiente',
            'completed': 'Completada',
            'cancelled': 'Cancelada',
            'refunded': 'Reembolsada'
        }
        
        payment_status_map = {
            'pending': 'Pendiente',
            'paid': 'Pagado',
            'failed': 'Fallido',
            'refunded': 'Reembolsado'
        }
        
        sale_details = [
            f"<b>Estado:</b> {status_map.get(sale.status, sale.status)}",
            f"<b>Estado de Pago:</b> {payment_status_map.get(sale.payment_status, sale.payment_status)}",
            f"<b>Total de Items:</b> {sale.total_items}",
        ]
        
        if sale.notes:
            sale_details.append(f"<b>Notas:</b> {sale.notes}")
        
        for detail in sale_details:
            elements.append(Paragraph(detail, self.styles['Normal']))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_products_table(self, sale):
        """Crear tabla de productos"""
        elements = []
        
        elements.append(Paragraph("PRODUCTOS", self.styles['CustomSubtitle']))
        
        # Datos de la tabla
        data = [['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]
        
        for item in sale.items.all():
            data.append([
                item.product.name,
                str(item.quantity),
                f"${item.price:.2f}",
                f"${item.subtotal:.2f}"
            ])
        
        # Crear tabla
        table = Table(data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_totals(self, sale):
        """Crear sección de totales"""
        elements = []
        
        # Tabla de totales
        totals_data = [
            ['Subtotal:', f"${sale.subtotal:.2f}"],
            ['Descuento:', f"${sale.discount:.2f}"],
            ['TOTAL:', f"${sale.total:.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[2*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.darkblue),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.darkblue),
        ]))
        
        elements.append(totals_table)
        elements.append(Spacer(1, 30))
        return elements
    
    def _create_footer(self):
        """Crear pie de página"""
        elements = []
        
        elements.append(Paragraph("¡Gracias por su compra!", self.styles['Normal']))
        elements.append(Paragraph("Este documento es una nota de venta generada automáticamente por SmartSales365", self.styles['CompanyInfo']))
        
        return elements


def generate_sale_receipt_pdf(sale):
    """Función helper para generar PDF de nota de venta"""
    service = SaleReceiptPDFService()
    return service.generate_sale_receipt(sale)
