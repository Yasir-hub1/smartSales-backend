from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    list_filter = ['created_at', 'is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'stock', 'category', 'created_at']
    list_filter = ['category', 'is_digital', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['profit_margin']
