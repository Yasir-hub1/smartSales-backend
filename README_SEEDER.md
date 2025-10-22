# 🌱 Seeder de Electrodomésticos - SmartSales365

Este documento describe los scripts de seeder disponibles para poblar la base de datos con datos de electrodomésticos.

## 📋 Scripts Disponibles

### 1. **Seeder Principal** (`seed_electrodomesticos.py`)
Script completo que limpia y puebla la base de datos con datos de electrodomésticos.

```bash
# Limpiar y poblar con datos por defecto
python seed_electrodomesticos.py

# Limpiar y poblar con parámetros personalizados
python manage.py seed_electrodomesticos --clean --products 100 --clients 100 --sales 500
```

### 2. **Comando Django** (`manage.py seed_electrodomesticos`)
Comando de Django para gestionar datos desde la línea de comandos.

```bash
# Opciones disponibles
python manage.py seed_electrodomesticos --help

# Ejemplos de uso
python manage.py seed_electrodomesticos --clean --products 50 --clients 50 --sales 200
python manage.py seed_electrodomesticos --products 100 --clients 100 --sales 500
```

### 3. **Gestión de Datos** (`manage_data.py`)
Script interactivo para gestionar la base de datos.

```bash
# Modo interactivo
python manage_data.py

# Comandos directos
python manage_data.py stats    # Mostrar estadísticas
python manage_data.py clean    # Limpiar base de datos
python manage_data.py seed     # Poblar datos
python manage_data.py reset    # Reset completo
```

### 4. **Generar Más Datos** (`generate_more_data.py`)
Script para agregar más datos sin limpiar la base de datos existente.

```bash
python generate_more_data.py
```

## 🏠 Datos Generados

### **Categorías de Electrodomésticos (10 principales)**
1. **Refrigeradores** - Refrigeradores y congeladores
2. **Lavadoras** - Lavadoras automáticas y semiautomáticas
3. **Secadoras** - Secadoras eléctricas y a gas
4. **Estufas y Hornos** - Estufas, hornos y microondas
5. **Aires Acondicionados** - Sistemas de climatización
6. **Televisores** - Smart TV de todas las tecnologías
7. **Audio y Sonido** - Sistemas de audio y sonido
8. **Pequeños Electrodomésticos** - Electrodomésticos pequeños
9. **Computadoras y Laptops** - Equipos de cómputo
10. **Celulares y Accesorios** - Teléfonos móviles

### **Productos por Categoría**
- **Refrigeradores**: 10 productos (Samsung, LG, Mabe, Whirlpool, etc.)
- **Lavadoras**: 10 productos (Samsung, LG, Mabe, Whirlpool, etc.)
- **Televisores**: 10 productos (Smart TV 4K, 8K, OLED, QLED)
- **Aires Acondicionados**: 10 productos (Minisplits, Ventana)
- **Computadoras**: 10 productos (Laptops, Desktops, MacBook, etc.)

### **Marcas Incluidas**
Samsung, LG, Sony, Panasonic, Toshiba, Hitachi, Daikin, Mabe, Whirlpool, Maytag, GE, Frigidaire, KitchenAid, Bosch, Electrolux, Haier, TCL, Hisense, Vizio, Apple, Dell, HP, Lenovo, Asus, Acer, MSI

### **Datos de Clientes**
- **50 clientes** con nombres mexicanos reales
- **Direcciones** en ciudades mexicanas
- **Tipos**: Individual y Empresa
- **Segmentos**: Nuevo, Regular, VIP
- **Datos completos**: Email, teléfono, dirección, ciudad, CP

### **Datos de Ventas**
- **200 ventas** distribuidas desde 2023 hasta ahora
- **Estados**: Completadas, Pendientes, Canceladas
- **Pagos**: Pagado, Parcial, Pendiente
- **Productos**: 1-5 productos por venta
- **Descuentos**: 0-20% aleatorio
- **Impuestos**: 16% (IVA mexicano)

## 📊 Estadísticas Generadas

### **Datos Base**
- 🏢 **Empresas**: 1 (ElectroDomésticos Pro)
- 👤 **Usuarios**: 5 (admin, gerente, vendedores, cajero)
- 📁 **Categorías**: 57 (10 principales + 47 subcategorías)
- 📦 **Productos**: 50+ (electrodomésticos variados)
- 👥 **Clientes**: 50+ (nombres mexicanos reales)
- 💰 **Ventas**: 200+ (distribuidas en el tiempo)
- 📋 **Items de venta**: 600+ (productos vendidos)

### **Métricas de Negocio**
- **Total de ventas**: $18,822,915.83 MXN
- **Ventas completadas**: 53 (26.5%)
- **Productos más vendidos**: Smart TV Sony 65" 4K UHD (46 unidades)
- **Distribución geográfica**: 40+ ciudades mexicanas
- **Período de datos**: Enero 2023 - Octubre 2025

## 🚀 Uso Rápido

### **Configuración Inicial**
```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Ejecutar seeder completo
python manage.py seed_electrodomesticos --clean --products 50 --clients 50 --sales 200

# 3. Verificar datos
python manage_data.py stats
```

### **Agregar Más Datos**
```bash
# Generar más productos, clientes y ventas
python generate_more_data.py

# Ver estadísticas actualizadas
python manage_data.py stats
```

### **Gestión Interactiva**
```bash
# Menú interactivo
python manage_data.py
```

## 🔧 Parámetros Personalizables

### **Seeder Principal**
- `--products`: Número de productos (default: 50)
- `--clients`: Número de clientes (default: 50)
- `--sales`: Número de ventas (default: 200)
- `--clean`: Limpiar base de datos antes de poblar

### **Ejemplos de Uso**
```bash
# Datos básicos
python manage.py seed_electrodomesticos --clean

# Datos extensos
python manage.py seed_electrodomesticos --clean --products 100 --clients 100 --sales 500

# Solo agregar datos (sin limpiar)
python manage.py seed_electrodomesticos --products 50 --clients 50 --sales 100
```

## 📈 Beneficios del Seeder

### **Para Desarrollo**
- ✅ **Datos realistas** de electrodomésticos
- ✅ **Relaciones consistentes** entre modelos
- ✅ **Datos históricos** desde 2023
- ✅ **Variedad geográfica** (ciudades mexicanas)
- ✅ **Datos de prueba** para ML y predicciones

### **Para Testing**
- ✅ **Casos de prueba** diversos
- ✅ **Datos de ventas** realistas
- ✅ **Clientes variados** (tipos y segmentos)
- ✅ **Productos diversos** (precios y categorías)
- ✅ **Estados de venta** variados

### **Para Demostraciones**
- ✅ **Dashboard funcional** con datos reales
- ✅ **Gráficas pobladas** con información
- ✅ **Predicciones ML** con datos históricos
- ✅ **Reportes completos** con información
- ✅ **Sistema completo** operativo

## 🎯 Próximos Pasos

1. **Ejecutar seeder** con datos de electrodomésticos
2. **Verificar dashboard** de predicciones
3. **Probar funcionalidades** ML
4. **Generar reportes** con datos reales
5. **Demostrar sistema** completo

---

**¡El sistema SmartSales365 está listo con datos realistas de electrodomésticos!** 🏠📱💻
