from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'models', views.MLModelViewSet)
router.register(r'predictions', views.PredictionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
