from django.urls import path
from . import views

urlpatterns = [
    # Clientes
    path('', views.ClientListCreateView.as_view(), name='client_list_create'),
    path('<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('<int:pk>/purchase-history/', views.client_purchase_history, name='client_purchase_history'),
    path('<int:pk>/update-segment/', views.update_client_segment, name='update_client_segment'),
    
    # Búsquedas y estadísticas
    path('search/', views.search_clients, name='search_clients'),
    path('stats/', views.client_stats, name='client_stats'),
    path('vip/', views.vip_clients, name='vip_clients'),
    path('new/', views.new_clients, name='new_clients'),
]