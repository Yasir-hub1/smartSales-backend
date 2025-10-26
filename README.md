# SmartSales365 - Backend

Sistema de gestión de ventas inteligente con capacidades de Machine Learning y análisis predictivo.

## Estructura del Proyecto

```
backend/
├── config/                 # Configuración del proyecto
│   ├── settings/
│   │   ├── base.py        # Configuración base
│   │   ├── development.py # Configuración de desarrollo
│   │   └── production.py  # Configuración de producción
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Configuración WSGI
├── apps/                  # Aplicaciones Django
│   ├── core/              # Modelos base y utilidades
│   ├── products/          # Gestión de productos
│   ├── clients/           # Gestión de clientes
│   ├── sales/             # Gestión de ventas
│   ├── payments/          # Integración de pagos
│   ├── reports/           # Motor de reportes
│   ├── ml_predictions/    # Servicio de ML
│   └── notifications/     # Notificaciones push
├── ml_models/             # Modelos ML serializados
├── media/                 # Archivos multimedia
├── static/               # Archivos estáticos
├── templates/            # Plantillas HTML
└── logs/                # Archivos de log
```

## Características

- **Gestión de Productos**: Catálogo completo con categorías y control de stock
- **Gestión de Clientes**: Base de datos de clientes con segmentación
- **Sistema de Ventas**: Carrito de compras y procesamiento de órdenes
- **Integración de Pagos**: PayPal, Stripe y otros métodos
- **Reportes Dinámicos**: Generación automática de reportes
- **Machine Learning**: Predicciones y recomendaciones inteligentes
- **Notificaciones**: Sistema de notificaciones push
- **API REST**: API completa con Django REST Framework

## Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd SmartSales365/backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

## Configuración

### Variables de Entorno

- `SECRET_KEY`: Clave secreta de Django
- `DEBUG`: Modo debug (True/False)
- `DATABASE_URL`: URL de la base de datos
- `REDIS_URL`: URL de Redis para cache
- `EMAIL_*`: Configuración de email
- `STRIPE_*`: Claves de Stripe
- `PAYPAL_*`: Credenciales de PayPal
- `FIREBASE_CREDENTIALS_PATH`: Ruta a credenciales de Firebase

### Configuración de Base de Datos

El proyecto soporta múltiples bases de datos:
- SQLite (desarrollo)
- PostgreSQL (producción)
- MySQL (opcional)

### Configuración de Cache

- Redis para cache y sesiones
- Cache de consultas de base de datos
- Cache de resultados de ML

## API Endpoints

### Core
- `GET /api/v1/health/` - Health check
- `GET /api/v1/companies/` - Lista de empresas
- `GET /api/v1/profiles/` - Perfiles de usuario

### Productos
- `GET /api/v1/products/categories/` - Categorías
- `GET /api/v1/products/products/` - Productos

### Clientes
- `GET /api/v1/clients/clients/` - Lista de clientes

### Ventas
- `GET /api/v1/sales/sales/` - Lista de ventas

### Pagos
- `GET /api/v1/payments/payments/` - Lista de pagos

### Reportes
- `GET /api/v1/reports/reports/` - Lista de reportes

### ML
- `GET /api/v1/ml/models/` - Modelos ML
- `GET /api/v1/ml/predictions/` - Predicciones

### Notificaciones
- `GET /api/v1/notifications/notifications/` - Notificaciones

## Desarrollo

### Estructura de Aplicaciones

Cada aplicación sigue el patrón Django estándar:
- `models.py`: Modelos de base de datos
- `views.py`: Vistas y lógica de negocio
- `serializers.py`: Serializadores para API
- `urls.py`: Configuración de URLs
- `admin.py`: Configuración del admin
- `apps.py`: Configuración de la aplicación

### Patrones de Diseño

- **Repository Pattern**: Para acceso a datos
- **Service Layer**: Para lógica de negocio
- **Factory Pattern**: Para creación de objetos
- **Observer Pattern**: Para notificaciones

### Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests específicos
python manage.py test apps.core.tests

# Con coverage
coverage run --source='.' manage.py test
coverage report
```

## Despliegue

### Desarrollo
```bash
python manage.py runserver
```

### Producción
```bash
# Con Gunicorn
gunicorn config.wsgi:application

# Con Docker
docker build -t SmartSales365-backend .
docker run -p 8000:8000 SmartSales365-backend
```

## Monitoreo

- **Logs**: Sistema de logging configurado
- **Sentry**: Monitoreo de errores
- **Health Checks**: Endpoints de salud
- **Métricas**: Métricas de rendimiento

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.
