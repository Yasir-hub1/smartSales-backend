#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.test import Client
import json

User = get_user_model()

# Verificar usuario admin
print("=== Verificando usuario admin ===")
try:
    user = User.objects.get(username='admin')
    print(f"Usuario encontrado: {user.username}")
    print(f"Email: {user.email}")
    print(f"Activo: {user.is_active}")
    print(f"Is staff: {user.is_staff}")
    
    # Probar autenticación
    auth_user = authenticate(username='admin', password='admin123')
    if auth_user:
        print("✓ Autenticación exitosa con 'admin123'")
    else:
        print("✗ Autenticación fallida con 'admin123'")
        print("  Necesitas cambiar la contraseña:")
        print("  python manage.py changepassword admin")
        
except User.DoesNotExist:
    print("✗ Usuario 'admin' no existe")
    print("  Crear con: python manage.py createsuperuser")

# Probar endpoint
print("\n=== Probando endpoint ===")
client = Client()

# Test 1: Login correcto
print("\n1. Login con admin/admin123:")
response = client.post(
    '/api/v1/mobile/auth/login/',
    data=json.dumps({'username': 'admin', 'password': 'admin123'}),
    content_type='application/json'
)
print(f"   Status: {response.status_code}")
print(f"   Response: {json.dumps(response.json() if response.status_code != 400 else response.content.decode(), indent=2)}")

# Test 2: Login con password incorrecto
print("\n2. Login con password incorrecto:")
response = client.post(
    '/api/v1/mobile/auth/login/',
    data=json.dumps({'username': 'admin', 'password': 'wrong'}),
    content_type='application/json'
)
print(f"   Status: {response.status_code}")
print(f"   Response: {json.dumps(response.json() if response.status_code != 400 else response.content.decode(), indent=2)}")

# Test 3: Campos vacíos
print("\n3. Login con campos vacíos:")
response = client.post(
    '/api/v1/mobile/auth/login/',
    data=json.dumps({'username': '', 'password': ''}),
    content_type='application/json'
)
print(f"   Status: {response.status_code}")
try:
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except:
    print(f"   Response: {response.content.decode()}")

