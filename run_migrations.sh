#!/bin/bash
# Script para ejecutar migraciones de Django

echo "🔧 Ejecutando migraciones de Django..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
fi

# Ejecutar migraciones
echo "📦 Creando migraciones para mobile app..."
python manage.py makemigrations mobile

echo "📥 Aplicando migraciones..."
python manage.py migrate

echo "✅ Migraciones completadas!"

