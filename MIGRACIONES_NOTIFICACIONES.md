# 🔧 Migraciones para Notificaciones Push

## ❌ Error Detectado

El error que estás viendo:
```
django.db.utils.OperationalError: no such table: mobile_pushnotificationdevice
```

Indica que falta la tabla en la base de datos. Necesitas ejecutar las migraciones.

## ✅ Solución

### Opción 1: Ejecutar Migraciones Manualmente

1. **Activa el entorno virtual:**
```bash
cd backend
source venv/bin/activate  # En Mac/Linux
# o
venv\Scripts\activate  # En Windows
```

2. **Crea las migraciones (si es necesario):**
```bash
python manage.py makemigrations mobile
```

3. **Aplica las migraciones:**
```bash
python manage.py migrate mobile
```

O aplica todas las migraciones pendientes:
```bash
python manage.py migrate
```

### Opción 2: Usar el Script Automático

```bash
cd backend
./run_migrations.sh
```

## 📋 Verificación

Después de ejecutar las migraciones, verifica que la tabla se creó correctamente:

```bash
python manage.py shell
```

```python
from apps.mobile.models import PushNotificationDevice
print(PushNotificationDevice.objects.all().count())
```

O verifica en el admin de Django: http://localhost:8000/admin/

## 🚀 Próximos Pasos

Una vez aplicadas las migraciones:

1. Reinicia el servidor Django
2. Vuelve a intentar registrar el dispositivo desde la app móvil
3. Verifica que el registro funcione correctamente

## 📝 Nota

Si tienes problemas con el entorno virtual, asegúrate de:
- Estar en el directorio `backend`
- Tener Django instalado en el entorno virtual
- Estar usando la versión correcta de Python

