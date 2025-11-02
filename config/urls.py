"""
URL configuration for SmartSales365.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API endpoints
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/clients/', include('apps.clients.urls')),
    path('api/v1/sales/', include('apps.sales.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/ml/', include('apps.ml_predictions.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    
    # API Móvil (endpoints separados para la app)
    path('api/v1/mobile/', include('apps.mobile.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
