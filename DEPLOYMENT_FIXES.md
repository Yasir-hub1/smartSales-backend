# 🔧 Correcciones para Producción - Endpoints API

## 🐛 Problemas Identificados

1. **`/api/v1/` da 404**: La ruta raíz no existe porque `apps.core.urls` no tiene una vista en la raíz
2. **`/api/v1/sales/` da 404**: Posible problema de configuración de URLs o servidor web
3. **ALLOWED_HOSTS**: Ya corregido - ahora incluye la IP del servidor por defecto
4. **SECURE_SSL_REDIRECT**: Ya corregido - ahora es configurable

## ✅ Correcciones Aplicadas

### 1. **ALLOWED_HOSTS** (production.py)
```python
# Antes:
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Después:
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ['24.144.94.118', 'localhost', '127.0.0.1']
```

### 2. **SECURE_SSL_REDIRECT** (production.py)
```python
# Antes:
SECURE_SSL_REDIRECT = True

# Después:
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
```

## 🔍 Diagnóstico de las Pruebas

### Endpoints que FUNCIONAN:
- ✅ `/admin/` - 200 OK
- ✅ `/api/v1/auth/login/` - 401 (normal, necesita credenciales)
- ✅ `/api/v1/products/` - 401 (normal, necesita autenticación)
- ✅ `/api/v1/mobile/products/dashboard/` - 401 (normal, necesita autenticación)

### Endpoints que dan 404:
- ❌ `/api/v1/` - 404 (no hay vista en la raíz, es normal)
- ❌ `/api/v1/sales/` - 404 (PROBLEMA - debería existir)

## 🚨 Problema Principal: `/api/v1/sales/` da 404

Esto puede ser causado por:

1. **Configuración de nginx**: El proxy puede no estar pasando correctamente las rutas
2. **URLs de sales**: Puede haber un problema en `apps/sales/urls.py`
3. **ROOT_URLCONF**: Verificar que esté usando `config.urls`

## 📋 Pasos para Resolver en el Servidor

1. **Verificar configuración de nginx**:
   ```nginx
   location /api/ {
       proxy_pass http://127.0.0.1:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
   }
   ```

2. **Verificar que Django esté usando `production.py`**:
   ```bash
   # En el servidor
   export DJANGO_SETTINGS_MODULE=config.settings.production
   ```

3. **Reiniciar servicios**:
   ```bash
   sudo systemctl restart gunicorn  # o uwsgi
   sudo systemctl restart nginx
   ```

4. **Verificar logs**:
   ```bash
   # Logs de nginx
   sudo tail -f /var/log/nginx/error.log
   
   # Logs de Django
   sudo tail -f /var/log/smartsales365/django.log
   ```

## 🔧 Solución Temporal

Si `/api/v1/` necesita responder algo, puedes agregar una vista simple en `apps/core/urls.py`:

```python
from django.http import JsonResponse
from django.urls import path

def api_root(request):
    return JsonResponse({
        'message': 'SmartSales365 API v1',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'products': '/api/v1/products/',
            'sales': '/api/v1/sales/',
            'mobile': '/api/v1/mobile/',
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    # ... resto de rutas
]
```

## ✅ Estado de Correcciones

- ✅ ALLOWED_HOSTS corregido
- ✅ SECURE_SSL_REDIRECT corregido  
- ⚠️  `/api/v1/sales/` necesita revisión en el servidor
- ✅ Script de prueba creado (`test_production_endpoints.py`)

