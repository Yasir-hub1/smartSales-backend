#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar el endpoint de login móvil
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.mobile.views import mobile_login
import json

User = get_user_model()

def test_login():
    """Probar el login con diferentes casos"""
    
    # Verificar si existe el usuario admin
    try:
        user = User.objects.get(username='admin')
        print(f"✓ Usuario 'admin' encontrado - Activo: {user.is_active}")
        print(f"  Email: {user.email}")
        print(f"  Verificar contraseña...")
        
        # Probar autenticación
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='admin', password='admin123')
        if auth_user:
            print(f"✓ Contraseña 'admin123' es válida")
        else:
            print(f"✗ Contraseña 'admin123' NO es válida")
            print(f"  Intenta cambiar la contraseña con: python manage.py changepassword admin")
    except User.DoesNotExist:
        print("✗ Usuario 'admin' no existe")
        print("  Crear con: python manage.py createsuperuser")
        return
    
    # Probar endpoint
    factory = RequestFactory()
    
    # Caso 1: Login correcto
    print("\n--- Test 1: Login correcto ---")
    request = factory.post(
        '/api/v1/mobile/auth/login/',
        data=json.dumps({'username': 'admin', 'password': 'admin123'}),
        content_type='application/json'
    )
    
    try:
        response = mobile_login(request)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.data}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Caso 2: Usuario incorrecto
    print("\n--- Test 2: Usuario incorrecto ---")
    request = factory.post(
        '/api/v1/mobile/auth/login/',
        data=json.dumps({'username': 'wrong', 'password': 'admin123'}),
        content_type='application/json'
    )
    
    try:
        response = mobile_login(request)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.data}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Caso 3: Campos vacíos
    print("\n--- Test 3: Campos vacíos ---")
    request = factory.post(
        '/api/v1/mobile/auth/login/',
        data=json.dumps({'username': '', 'password': ''}),
        content_type='application/json'
    )
    
    try:
        response = mobile_login(request)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.data}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    test_login()

