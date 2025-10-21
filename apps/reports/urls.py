"""
URLs para el módulo de reportes
"""
from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_reports, name='test_reports'),
    path('generate/', views.generate_report, name='generate_report'),
    path('templates/', views.get_report_templates, name='report_templates'),
    path('history/', views.get_report_history, name='report_history'),
    path('download/', views.download_report, name='download_report'),
]