from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    CustomTokenObtainPairView, 
    UserProfileView, 
    health_check, 
    dashboard_stats,
    api_root  # ← AGREGAR ESTE IMPORT
)
from .ai_views import chat_with_agent, process_voice_command, execute_agent_action, get_agent_suggestions

urlpatterns = [
    # Vista raíz de la API
    path('', api_root, name='api_root'),  # ← AGREGAR ESTA LÍNEA PRIMERO
    
    # Autenticación
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Dashboard
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    
    # Agente Inteligente
    path('ai/chat/', chat_with_agent, name='ai_chat'),
    path('ai/voice/', process_voice_command, name='ai_voice'),
    path('ai/action/', execute_agent_action, name='ai_action'),
    path('ai/suggestions/', get_agent_suggestions, name='ai_suggestions'),
]