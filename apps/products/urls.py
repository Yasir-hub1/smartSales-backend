from django.urls import path
from . import views

urlpatterns = [
    # Categorías
    path('categories/', views.CategoryListCreateView.as_view(), name='category_list_create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Productos
    path('', views.ProductListCreateView.as_view(), name='product_list_create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/stock/', views.update_product_stock, name='update_product_stock'),
    path('<int:pk>/price-history/', views.product_price_history, name='product_price_history'),
    
    # Búsquedas y estadísticas
    path('search/', views.search_products, name='search_products'),
    path('low-stock/', views.low_stock_products, name='low_stock_products'),
    path('stats/', views.product_stats, name='product_stats'),
]