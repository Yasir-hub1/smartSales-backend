from django.urls import path
from . import views

urlpatterns = [
    # Carritos
    path('carts/', views.CartListCreateView.as_view(), name='cart_list_create'),
    path('carts/<uuid:cart_id>/', views.CartDetailView.as_view(), name='cart_detail'),
    path('carts/<uuid:cart_id>/add/', views.add_to_cart, name='add_to_cart'),
    path('carts/<uuid:cart_id>/items/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('carts/<uuid:cart_id>/items/<int:item_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('carts/<uuid:cart_id>/clear/', views.clear_cart, name='clear_cart'),
    
    # Carrito del usuario
    path('cart/', views.get_user_cart, name='get_user_cart'),
    path('cart/create/', views.create_or_get_cart, name='create_or_get_cart'),
    path('cart/add-product/', views.add_product_to_cart, name='add_product_to_cart'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    
    # Ventas
    path('sales/', views.SaleListCreateView.as_view(), name='sale_list_create'),
    path('sales/<uuid:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('sales/from-cart/<uuid:cart_id>/', views.create_sale_from_cart, name='create_sale_from_cart'),
    
    # Estadísticas y reportes
    path('stats/', views.sale_stats, name='sale_stats'),
    path('sales-by-period/', views.sales_by_period, name='sales_by_period'),
    path('top-products/', views.top_products, name='top_products'),
    
    # Ventas públicas
    path('public-sales/', views.get_public_sales, name='get_public_sales'),
    path('sales-summary/', views.get_sales_summary, name='get_sales_summary'),
]