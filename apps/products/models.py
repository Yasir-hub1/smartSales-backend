from django.db import models
from apps.core.models import BaseModel


class Category(BaseModel):
    """Categorías de productos"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Categoría padre')
    image = models.ImageField(upload_to='categories/', blank=True, verbose_name='Imagen')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(BaseModel):
    """Productos del catálogo"""
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción')
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Costo')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    min_stock = models.PositiveIntegerField(default=0, verbose_name='Stock mínimo')
    max_stock = models.PositiveIntegerField(default=1000, verbose_name='Stock máximo')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Categoría')
    image = models.ImageField(upload_to='products/', blank=True, verbose_name='Imagen')
    is_digital = models.BooleanField(default=False, verbose_name='Producto digital')
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Peso (kg)')
    dimensions = models.CharField(max_length=100, blank=True, verbose_name='Dimensiones')
    barcode = models.CharField(max_length=50, blank=True, verbose_name='Código de barras')
    tags = models.CharField(max_length=500, blank=True, verbose_name='Etiquetas')
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def profit_margin(self):
        """Margen de ganancia"""
        if self.cost > 0:
            return ((self.price - self.cost) / self.cost) * 100
        return 0
    
    @property
    def is_low_stock(self):
        """Verifica si el stock está bajo"""
        return self.stock <= self.min_stock
    
    @property
    def stock_status(self):
        """Estado del stock"""
        if self.stock == 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'


class PriceHistory(BaseModel):
    """Historial de precios de productos"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history', verbose_name='Producto')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio anterior')
    new_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio nuevo')
    change_reason = models.CharField(max_length=200, blank=True, verbose_name='Motivo del cambio')
    
    class Meta:
        verbose_name = 'Historial de Precio'
        verbose_name_plural = 'Historial de Precios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.old_price} → {self.new_price}"
