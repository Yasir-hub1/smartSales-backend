#!/usr/bin/env python
"""
Script para configurar el proyecto SmartSales365
"""
import os
import sys
from pathlib import Path

def create_env_file():
    """Crea el archivo .env con las configuraciones"""
    env_content = """# Configuración local de SmartSales365

# Django
SECRET_KEY=django-insecure-!#&0snz7ndi_cm+iuby0a-hd_b!_sh4%955u-q*t3l2f8a$3o#
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos PostgreSQL
DB_NAME=salesmart
DB_USER=defectdojo
DB_PASSWORD=12345678
DB_HOST=localhost
DB_PORT=5433

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@smartsales365.com

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Pagos
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_secret

# Firebase (Notificaciones)
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json

# OpenAI (Reconocimiento de voz)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Sentry (Monitoreo)
SENTRY_DSN=your-sentry-dsn-here

# Configuración de ML
ML_MODELS_PATH=ml_models/
ML_RETRAIN_SCHEDULE=daily

# Configuración de reportes
REPORTS_PATH=media/reports/
REPORT_CACHE_TTL=3600

# Configuración de notificaciones
NOTIFICATION_BATCH_SIZE=100
NOTIFICATION_RATE_LIMIT=1000
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env creado")
    else:
        print("ℹ️  Archivo .env ya existe")

def main():
    """Función principal"""
    print("🚀 Configurando SmartSales365...")
    
    # Crear archivo .env
    create_env_file()
    
    print("\n📋 Pasos siguientes:")
    print("1. Asegúrate de que PostgreSQL esté ejecutándose en el puerto 5433")
    print("2. Crea la base de datos 'salesmart' si no existe:")
    print("   createdb -h localhost -p 5433 -U defectdojo salesmart")
    print("3. Ejecuta el script de configuración de la base de datos:")
    print("   python setup_db.py")
    print("4. Inicia el servidor:")
    print("   python manage.py runserver")
    print("\n🔗 URLs importantes:")
    print("   - Admin: http://localhost:8000/admin/")
    print("   - API Docs: http://localhost:8000/api/docs/")
    print("   - Health Check: http://localhost:8000/api/v1/health/")

if __name__ == '__main__':
    main()
