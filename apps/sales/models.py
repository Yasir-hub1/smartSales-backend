from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.products.models import Product
from apps.clients.models import Client
import uuid

class Cart(BaseModel):
    """Carrito de compras"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Cliente')
    session_key = models.CharField(max_length=100, blank=True, verbose_name='Clave de Sesión')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
    
    def __str__(self):
        return f"Carrito {self.id}"
    
    @property
    def total_items(self):
        """Total de items en el carrito"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_amount(self):
        """Total del carrito"""
        return sum(item.subtotal for item in self.items.all())
    
    def add_product(self, product, quantity=1):
        """Agregar producto al carrito"""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item
    
    def remove_product(self, product):
        """Remover producto del carrito"""
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False
    
    def clear(self):
        """Limpiar carrito"""
        self.items.all().delete()
    
    def update_quantity(self, product, quantity):
        """Actualizar cantidad de un producto"""
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            return True
        except CartItem.DoesNotExist:
            return False


class CartItem(BaseModel):
    """Items del carrito de compras"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Carrito')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto')
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    
    class Meta:
        verbose_name = 'Item del Carrito'
        verbose_name_plural = 'Items del Carrito'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        # Actualizar el precio al momento de guardar
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)


class Sale(BaseModel):
    """Ventas del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Cliente')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Vendedor')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal')
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Impuestos')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Descuento')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendiente'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('refunded', 'Reembolsada')
    ], default='pending', verbose_name='Estado')
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado')
    ], default='pending', verbose_name='Estado de Pago')
    notes = models.TextField(blank=True, verbose_name='Notas')
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name='ID de Transacción')
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Venta #{self.id}"
    
    @property
    def total_items(self):
        """Total de items en la venta"""
        return sum(item.quantity for item in self.items.all())
    
    def calculate_totals(self):
        """Calcular totales de la venta"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total = self.subtotal + self.tax - self.discount
        self.save()


class SaleItem(BaseModel):
    """Items de una venta"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name='Venta')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto')
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    
    class Meta:
        verbose_name = 'Item de Venta'
        verbose_name_plural = 'Items de Venta'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        return self.quantity * self.price


class SaleReceipt(BaseModel):
    """Comprobantes de venta"""
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='receipt', verbose_name='Venta')
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name='Número de Comprobante')
    pdf_file = models.FileField(upload_to='receipts/', blank=True, verbose_name='Archivo PDF')
    qr_code = models.TextField(blank=True, verbose_name='Código QR')
    
    class Meta:
        verbose_name = 'Comprobante de Venta'
        verbose_name_plural = 'Comprobantes de Venta'
    
    def __str__(self):
        return f"Comprobante {self.receipt_number}"
