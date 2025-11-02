from django.urls import path
from . import views

urlpatterns = [
    # Autenticación móvil
    path('auth/login/', views.mobile_login, name='mobile_login'),
    
    # Notificaciones Push
    path('notifications/register-device/', views.register_push_device, name='register_push_device'),
    path('notifications/unregister-device/<str:device_token>/', views.unregister_push_device, name='unregister_push_device'),
    path('notifications/send/', views.send_push_notification, name='send_push_notification'),
    
    # Dashboard de productos
    path('products/dashboard/', views.products_dashboard, name='mobile_products_dashboard'),
    path('products/download-template/', views.download_excel_template, name='mobile_download_excel_template'),
    path('products/preview-excel/', views.preview_excel, name='mobile_preview_excel'),
    path('products/import-excel/', views.import_products_excel, name='mobile_import_products_excel'),
    
    # Reportes
    path('reports/frequent-clients/', views.frequent_clients_report, name='mobile_frequent_clients_report'),
]

