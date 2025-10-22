#!/usr/bin/env python
"""
Seeder para datos de electrodomésticos
Crea categorías, productos, clientes y ventas desde 2023
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.core.models import User, Company
from apps.products.models import Category, Product
from apps.clients.models import Client
from apps.sales.models import Sale, SaleItem
from django.utils import timezone

User = get_user_model()

# Datos de categorías de electrodomésticos
CATEGORIAS_ELECTRODOMESTICOS = [
    {
        'name': 'Refrigeradores',
        'description': 'Refrigeradores y congeladores de todas las marcas y capacidades',
        'subcategories': [
            'Refrigeradores de Una Puerta',
            'Refrigeradores de Dos Puertas',
            'Refrigeradores Side by Side',
            'Congeladores Verticales',
            'Congeladores Horizontales'
        ]
    },
    {
        'name': 'Lavadoras',
        'description': 'Lavadoras automáticas y semiautomáticas',
        'subcategories': [
            'Lavadoras de Carga Superior',
            'Lavadoras de Carga Frontal',
            'Lavadoras de Doble Tina',
            'Centros de Lavado'
        ]
    },
    {
        'name': 'Secadoras',
        'description': 'Secadoras de ropa eléctricas y a gas',
        'subcategories': [
            'Secadoras Eléctricas',
            'Secadoras a Gas',
            'Centros de Lavado y Secado'
        ]
    },
    {
        'name': 'Estufas y Hornos',
        'description': 'Estufas, hornos y microondas',
        'subcategories': [
            'Estufas de Gas',
            'Estufas Eléctricas',
            'Hornos de Empotrar',
            'Microondas',
            'Hornos de Convección'
        ]
    },
    {
        'name': 'Aires Acondicionados',
        'description': 'Sistemas de climatización',
        'subcategories': [
            'Aires Acondicionados de Ventana',
            'Aires Acondicionados Portátiles',
            'Minisplits',
            'Aires Acondicionados Centrales'
        ]
    },
    {
        'name': 'Televisores',
        'description': 'Televisores y pantallas de todas las tecnologías',
        'subcategories': [
            'Smart TV LED',
            'Smart TV OLED',
            'Smart TV QLED',
            'Televisores 4K',
            'Televisores 8K'
        ]
    },
    {
        'name': 'Audio y Sonido',
        'description': 'Sistemas de audio y sonido',
        'subcategories': [
            'Bocinas Bluetooth',
            'Sistemas de Sonido',
            'Soundbars',
            'Auriculares',
            'Amplificadores'
        ]
    },
    {
        'name': 'Pequeños Electrodomésticos',
        'description': 'Electrodomésticos pequeños para el hogar',
        'subcategories': [
            'Licuadoras',
            'Batidoras',
            'Cafeteras',
            'Tostadores',
            'Planchas',
            'Aspiradoras'
        ]
    },
    {
        'name': 'Computadoras y Laptops',
        'description': 'Equipos de cómputo y accesorios',
        'subcategories': [
            'Laptops',
            'Computadoras de Escritorio',
            'Tablets',
            'Monitores',
            'Impresoras'
        ]
    },
    {
        'name': 'Celulares y Accesorios',
        'description': 'Teléfonos móviles y accesorios',
        'subcategories': [
            'Smartphones',
            'Fundas y Protectores',
            'Cargadores',
            'Auriculares',
            'Power Banks'
        ]
    }
]

# Marcas de electrodomésticos
MARCAS = [
    'Samsung', 'LG', 'Sony', 'Panasonic', 'Toshiba', 'Hitachi', 'Daikin',
    'Mabe', 'Whirlpool', 'Maytag', 'GE', 'Frigidaire', 'KitchenAid',
    'Bosch', 'Electrolux', 'Haier', 'TCL', 'Hisense', 'Vizio',
    'Apple', 'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'MSI'
]

# Nombres de productos por categoría
PRODUCTOS_POR_CATEGORIA = {
    'Refrigeradores': [
        'Refrigerador Samsung 2 Puertas 350L', 'Refrigerador LG Side by Side 600L',
        'Refrigerador Mabe 1 Puerta 250L', 'Congelador Whirlpool 200L',
        'Refrigerador Bosch 2 Puertas 400L', 'Refrigerador GE Side by Side 500L',
        'Refrigerador Frigidaire 1 Puerta 300L', 'Congelador Samsung 150L',
        'Refrigerador Haier 2 Puertas 320L', 'Refrigerador TCL 1 Puerta 280L'
    ],
    'Lavadoras': [
        'Lavadora Samsung 18kg Carga Superior', 'Lavadora LG 20kg Carga Frontal',
        'Lavadora Mabe 16kg Doble Tina', 'Lavadora Whirlpool 15kg Carga Superior',
        'Lavadora Bosch 12kg Carga Frontal', 'Lavadora GE 14kg Carga Superior',
        'Lavadora Frigidaire 16kg Carga Frontal', 'Lavadora Haier 18kg Carga Superior',
        'Lavadora TCL 15kg Carga Frontal', 'Lavadora Electrolux 17kg Carga Superior'
    ],
    'Secadoras': [
        'Secadora Samsung 20kg Eléctrica', 'Secadora LG 18kg a Gas',
        'Secadora Whirlpool 15kg Eléctrica', 'Secadora Bosch 12kg Eléctrica',
        'Secadora GE 16kg a Gas', 'Secadora Frigidaire 14kg Eléctrica',
        'Secadora Haier 18kg Eléctrica', 'Secadora Electrolux 16kg a Gas',
        'Secadora Mabe 15kg Eléctrica', 'Secadora TCL 17kg Eléctrica'
    ],
    'Estufas y Hornos': [
        'Estufa Samsung 4 Quemadores Gas', 'Estufa LG 6 Quemadores Eléctrica',
        'Estufa Mabe 4 Quemadores Gas', 'Horno Samsung 30L Eléctrico',
        'Microondas LG 25L 1000W', 'Horno Whirlpool 30L Eléctrico',
        'Estufa Bosch 5 Quemadores Gas', 'Microondas Samsung 28L 1200W',
        'Horno GE 30L Eléctrico', 'Estufa Frigidaire 4 Quemadores Gas'
    ],
    'Aires Acondicionados': [
        'Minisplit Samsung 1.5 Ton 12000 BTU', 'Aire LG 1 Ton 9000 BTU',
        'Minisplit Daikin 2 Ton 18000 BTU', 'Aire Samsung 1.5 Ton Ventana',
        'Minisplit Mabe 1 Ton 12000 BTU', 'Aire Whirlpool 1.5 Ton Ventana',
        'Minisplit Bosch 2 Ton 18000 BTU', 'Aire GE 1 Ton 9000 BTU',
        'Minisplit Haier 1.5 Ton 12000 BTU', 'Aire TCL 1 Ton Ventana'
    ],
    'Televisores': [
        'Smart TV Samsung 55" 4K UHD', 'Smart TV LG 65" OLED 4K',
        'Smart TV Sony 50" 4K UHD', 'Smart TV TCL 43" 4K UHD',
        'Smart TV Hisense 55" 4K UHD', 'Smart TV Vizio 50" 4K UHD',
        'Smart TV Samsung 75" 8K QLED', 'Smart TV LG 48" OLED 4K',
        'Smart TV Sony 65" 4K UHD', 'Smart TV TCL 32" HD Ready'
    ],
    'Audio y Sonido': [
        'Bocina Bluetooth Sony SRS-XB43', 'Soundbar Samsung HW-Q60T',
        'Sistema de Sonido LG LHB675N', 'Bocina Bluetooth JBL Charge 4',
        'Soundbar LG SN4A', 'Auriculares Sony WH-1000XM4',
        'Bocina Bluetooth Bose SoundLink', 'Soundbar Samsung HW-T450',
        'Sistema de Sonido Panasonic SC-UA7', 'Bocina Bluetooth Anker Soundcore'
    ],
    'Pequeños Electrodomésticos': [
        'Licuadora Oster 450W 6 Velocidades', 'Batidora KitchenAid 5KSM150',
        'Cafetera Keurig K-Elite', 'Tostador Black+Decker TR3500',
        'Plancha Rowenta DW5080', 'Aspiradora Dyson V11 Absolute',
        'Licuadora Ninja BL610', 'Cafetera Nespresso Vertuo',
        'Batidora Hamilton Beach 62650', 'Aspiradora Shark Navigator'
    ],
    'Computadoras y Laptops': [
        'Laptop Dell Inspiron 15 3000', 'Laptop HP Pavilion 15',
        'Laptop Lenovo IdeaPad 3', 'Laptop Asus VivoBook 15',
        'Laptop Acer Aspire 5', 'Desktop Dell OptiPlex 7090',
        'Laptop MacBook Air M1', 'Laptop MSI Gaming GF63',
        'Desktop HP Pavilion Desktop', 'Laptop Lenovo ThinkPad E15'
    ],
    'Celulares y Accesorios': [
        'iPhone 13 Pro 128GB', 'Samsung Galaxy S21 128GB',
        'iPhone 12 64GB', 'Samsung Galaxy A52 128GB',
        'iPhone 11 64GB', 'Samsung Galaxy S20 FE 128GB',
        'Fundas iPhone 13 Pro', 'Cargadores USB-C Rápidos',
        'Auriculares AirPods Pro', 'Power Bank Anker 20000mAh'
    ]
}

# Nombres de clientes
NOMBRES_CLIENTES = [
    'Ana García López', 'Carlos Rodríguez Martínez', 'María Fernández González',
    'José Luis Hernández Pérez', 'Carmen Sánchez Ruiz', 'Miguel Ángel Torres Díaz',
    'Isabel Morales Jiménez', 'Francisco Javier Vázquez Castro', 'Laura Patricia Flores Vega',
    'Roberto Carlos Mendoza Silva', 'Patricia Elena Herrera Rojas', 'Antonio Manuel Cruz Ramos',
    'Sandra Luz Guerrero Morales', 'Fernando Alberto Peña Delgado', 'Mónica Alejandra Reyes Ortega',
    'Ricardo Eduardo Vargas Luna', 'Claudia Beatriz Medina Herrera', 'Alejandro José Castillo Flores',
    'Verónica Patricia Ramírez Aguilar', 'Eduardo Antonio Vega Mendoza', 'Gabriela Alejandra Solís Torres',
    'Manuel Francisco Gutiérrez Ríos', 'Adriana Patricia Navarro Castro', 'Jorge Luis Espinoza Herrera',
    'Norma Alicia Jiménez Flores', 'Héctor Manuel Delgado Rojas', 'Silvia Patricia Luna Morales',
    'Raúl Eduardo Herrera Vega', 'María del Carmen Flores Mendoza', 'Carlos Alberto Torres Silva',
    'Leticia Patricia Rojas Castro', 'Fernando José Medina Herrera', 'Alejandra Patricia Vega Flores',
    'Roberto Carlos Silva Torres', 'Patricia Elena Castro Rojas', 'Antonio Manuel Herrera Flores',
    'Sandra Luz Vega Mendoza', 'Fernando Alberto Torres Silva', 'Mónica Alejandra Castro Rojas',
    'Ricardo Eduardo Herrera Flores', 'Claudia Beatriz Vega Torres', 'Alejandro José Silva Castro',
    'Verónica Patricia Rojas Herrera', 'Eduardo Antonio Flores Vega', 'Gabriela Alejandra Torres Silva',
    'Manuel Francisco Castro Rojas', 'Adriana Patricia Herrera Flores', 'Jorge Luis Vega Torres',
    'Norma Alicia Silva Castro', 'Héctor Manuel Rojas Herrera'
]

# Ciudades mexicanas
CIUDADES = [
    'Ciudad de México', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana',
    'León', 'Juárez', 'Torreón', 'Querétaro', 'San Luis Potosí',
    'Mérida', 'Mexicali', 'Aguascalientes', 'Acapulco', 'Culiacán',
    'Saltillo', 'Hermosillo', 'Villahermosa', 'Chihuahua', 'Reynosa',
    'Tampico', 'Irapuato', 'Matamoros', 'Durango', 'Tuxtla Gutiérrez',
    'Ensenada', 'Xalapa', 'Mazatlán', 'Nuevo Laredo', 'Oaxaca',
    'Campeche', 'Chetumal', 'Colima', 'Toluca', 'Cuernavaca',
    'Tlaxcala', 'Pachuca', 'Chilpancingo', 'Zacatecas', 'La Paz'
]

def crear_categorias():
    """Crear categorías de electrodomésticos"""
    print("🏠 Creando categorías de electrodomésticos...")
    
    categorias_creadas = []
    
    for cat_data in CATEGORIAS_ELECTRODOMESTICOS:
        categoria = Category.objects.create(
            name=cat_data['name'],
            description=cat_data['description'],
            is_active=True
        )
        categorias_creadas.append(categoria)
        print(f"  ✅ Categoría creada: {categoria.name}")
        
        # Crear subcategorías
        for subcat_name in cat_data['subcategories']:
            subcategoria = Category.objects.create(
                name=subcat_name,
                description=f"Subcategoría de {cat_data['name']}",
                parent=categoria,
                is_active=True
            )
            print(f"    📁 Subcategoría: {subcat_name}")
    
    return categorias_creadas

def crear_productos(categorias):
    """Crear productos de electrodomésticos"""
    print("📦 Creando productos de electrodomésticos...")
    
    productos_creados = []
    sku_counter = 1000
    
    for categoria in categorias:
        if categoria.name in PRODUCTOS_POR_CATEGORIA:
            productos_nombres = PRODUCTOS_POR_CATEGORIA[categoria.name]
            
            for i, nombre_producto in enumerate(productos_nombres):
                # Precio base según categoría
                if 'Refrigerador' in categoria.name:
                    precio_base = random.randint(8000, 25000)
                elif 'Lavadora' in categoria.name or 'Secadora' in categoria.name:
                    precio_base = random.randint(5000, 15000)
                elif 'TV' in categoria.name or 'Televisor' in categoria.name:
                    precio_base = random.randint(3000, 50000)
                elif 'Aire' in categoria.name:
                    precio_base = random.randint(3000, 12000)
                elif 'Laptop' in categoria.name or 'Computadora' in categoria.name:
                    precio_base = random.randint(8000, 35000)
                elif 'iPhone' in nombre_producto or 'Samsung Galaxy' in nombre_producto:
                    precio_base = random.randint(15000, 35000)
                else:
                    precio_base = random.randint(500, 5000)
                
                # Generar SKU único
                sku = f"ELEC-{sku_counter:06d}"
                sku_counter += 1
                
                # Calcular costo (70-85% del precio)
                costo = Decimal(str(precio_base * random.uniform(0.70, 0.85)))
                precio = Decimal(str(precio_base))
                
                # Stock aleatorio
                stock = random.randint(0, 50)
                min_stock = random.randint(5, 15)
                max_stock = random.randint(50, 100)
                
                # Peso y dimensiones
                peso = Decimal(str(random.uniform(1.0, 50.0)))
                dimensiones = f"{random.randint(30, 80)}x{random.randint(30, 60)}x{random.randint(30, 100)} cm"
                
                # Código de barras
                barcode = f"7{random.randint(100000000000, 999999999999)}"
                
                # Tags
                tags = f"{categoria.name}, {random.choice(MARCAS)}, electrodoméstico"
                
                producto = Product.objects.create(
                    name=nombre_producto,
                    description=f"Descripción detallada del {nombre_producto}. Producto de alta calidad con garantía del fabricante.",
                    sku=sku,
                    price=precio,
                    cost=costo,
                    stock=stock,
                    min_stock=min_stock,
                    max_stock=max_stock,
                    category=categoria,
                    weight=peso,
                    dimensions=dimensiones,
                    barcode=barcode,
                    tags=tags,
                    is_digital=False
                )
                
                productos_creados.append(producto)
                print(f"  ✅ Producto: {producto.name} - ${producto.price}")
    
    return productos_creados

def crear_clientes():
    """Crear clientes"""
    print("👥 Creando clientes...")
    
    clientes_creados = []
    
    for i, nombre in enumerate(NOMBRES_CLIENTES):
        # Generar email único
        email = f"cliente{i+1}@email.com"
        
        # Teléfono aleatorio
        telefono = f"55{random.randint(10000000, 99999999)}"
        
        # Dirección aleatoria
        calles = ['Av. Reforma', 'Calle Juárez', 'Av. Insurgentes', 'Calle Hidalgo', 'Av. Chapultepec']
        numeros = random.randint(100, 9999)
        direccion = f"{random.choice(calles)} {numeros}, Col. Centro"
        
        # Ciudad aleatoria
        ciudad = random.choice(CIUDADES)
        
        # Código postal
        cp = f"{random.randint(10000, 99999)}"
        
        # Tipo de cliente
        tipo_cliente = random.choice(['individual', 'business'])
        
        # Segmento basado en total de compras (se actualizará después)
        segmento = random.choice(['new', 'regular', 'vip'])
        
        # Fecha de nacimiento (entre 18 y 80 años)
        fecha_nacimiento = datetime.now() - timedelta(days=random.randint(18*365, 80*365))
        
        cliente = Client.objects.create(
            name=nombre,
            email=email,
            phone=telefono,
            address=direccion,
            city=ciudad,
            postal_code=cp,
            client_type=tipo_cliente,
            segment=segmento,
            birth_date=fecha_nacimiento.date(),
            notes=f"Cliente {tipo_cliente} de {ciudad}",
            is_active=True
        )
        
        clientes_creados.append(cliente)
        print(f"  ✅ Cliente: {cliente.name} - {cliente.email}")
    
    return clientes_creados

def crear_usuarios():
    """Crear usuarios del sistema"""
    print("👤 Creando usuarios del sistema...")
    
    usuarios_creados = []
    
    # Usuarios predefinidos
    usuarios_data = [
        {
            'username': 'admin',
            'email': 'admin@smartsales365.com',
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'gerente',
            'email': 'gerente@smartsales365.com',
            'first_name': 'María',
            'last_name': 'González',
            'role': 'manager',
            'is_staff': True
        },
        {
            'username': 'vendedor1',
            'email': 'vendedor1@smartsales365.com',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'role': 'seller'
        },
        {
            'username': 'vendedor2',
            'email': 'vendedor2@smartsales365.com',
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'role': 'seller'
        },
        {
            'username': 'cajero1',
            'email': 'cajero1@smartsales365.com',
            'first_name': 'Luis',
            'last_name': 'Hernández',
            'role': 'cashier'
        }
    ]
    
    for user_data in usuarios_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'is_staff': user_data.get('is_staff', False),
                'is_superuser': user_data.get('is_superuser', False),
                'is_active': True
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print(f"  ✅ Usuario creado: {user.username} ({user.role})")
        else:
            print(f"  ⚠️ Usuario ya existe: {user.username}")
        
        usuarios_creados.append(user)
    
    return usuarios_creados

def crear_ventas(clientes, productos, usuarios):
    """Crear ventas desde 2023"""
    print("💰 Creando ventas desde 2023...")
    
    ventas_creadas = []
    
    # Fecha de inicio: 1 de enero de 2023
    fecha_inicio = datetime(2023, 1, 1)
    fecha_actual = datetime.now()
    
    # Crear 200 ventas distribuidas en el tiempo
    for i in range(200):
        # Fecha aleatoria entre 2023 y ahora
        dias_diferencia = (fecha_actual - fecha_inicio).days
        dias_aleatorios = random.randint(0, dias_diferencia)
        fecha_venta = fecha_inicio + timedelta(days=dias_aleatorios)
        
        # Cliente aleatorio
        cliente = random.choice(clientes)
        
        # Usuario aleatorio (vendedor)
        usuario = random.choice([u for u in usuarios if u.role in ['seller', 'manager']])
        
        # Productos aleatorios (1-5 productos por venta)
        num_productos = random.randint(1, 5)
        productos_venta = random.sample(productos, num_productos)
        
        # Calcular totales
        subtotal = Decimal('0')
        items_venta = []
        
        for producto in productos_venta:
            cantidad = random.randint(1, 3)
            precio = producto.price
            subtotal_item = precio * cantidad
            subtotal += subtotal_item
            
            items_venta.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal_item
            })
        
        # Impuestos (16%)
        tax = subtotal * Decimal('0.16')
        
        # Descuento aleatorio (0-20%)
        descuento_porcentaje = random.randint(0, 20)
        descuento = subtotal * Decimal(str(descuento_porcentaje / 100))
        
        # Total final
        total = subtotal + tax - descuento
        
        # Estado de la venta
        estado = random.choice(['completed', 'pending', 'cancelled'])
        if estado == 'completed':
            payment_status = random.choice(['paid', 'partial'])
        else:
            payment_status = 'pending'
        
        # Crear venta
        venta = Sale.objects.create(
            client=cliente,
            user=usuario,
            subtotal=subtotal,
            tax=tax,
            discount=descuento,
            total=total,
            status=estado,
            payment_status=payment_status,
            notes=f"Venta generada automáticamente - {fecha_venta.strftime('%Y-%m-%d')}",
            transaction_id=f"TXN-{random.randint(100000, 999999)}"
        )
        
        # Crear items de la venta
        for item_data in items_venta:
            SaleItem.objects.create(
                sale=venta,
                product=item_data['producto'],
                quantity=item_data['cantidad'],
                price=item_data['precio']
            )
        
        ventas_creadas.append(venta)
        
        # Actualizar estadísticas del cliente
        if estado == 'completed':
            cliente.total_purchases += total
            if not cliente.last_purchase_date or fecha_venta > cliente.last_purchase_date:
                cliente.last_purchase_date = timezone.make_aware(fecha_venta)
            cliente.save()
        
        if i % 50 == 0:
            print(f"  ✅ Creadas {i+1} ventas...")
    
    print(f"  ✅ Total de ventas creadas: {len(ventas_creadas)}")
    return ventas_creadas

def crear_empresa():
    """Crear información de la empresa"""
    print("🏢 Creando información de la empresa...")
    
    empresa, created = Company.objects.get_or_create(
        name='ElectroDomésticos Pro',
        defaults={
            'legal_name': 'ElectroDomésticos Pro S.A. de C.V.',
            'rfc': 'EDP123456789',
            'address': 'Av. Tecnología 123, Col. Digital, Ciudad de México',
            'phone': '+52 55 1234 5678',
            'email': 'info@electrodomesticospro.com',
            'website': 'https://electrodomesticospro.com',
            'tax_rate': 16.0,
            'currency': 'MXN',
            'timezone': 'America/Mexico_City'
        }
    )
    
    if created:
        print(f"  ✅ Empresa creada: {empresa.name}")
    else:
        print(f"  ⚠️ Empresa ya existe: {empresa.name}")
    
    return empresa

def main():
    """Función principal del seeder"""
    print("🚀 Iniciando seeder de electrodomésticos...")
    print("=" * 60)
    
    try:
        # Crear empresa
        empresa = crear_empresa()
        
        # Crear categorías
        categorias = crear_categorias()
        
        # Crear productos
        productos = crear_productos(categorias)
        
        # Crear usuarios
        usuarios = crear_usuarios()
        
        # Crear clientes
        clientes = crear_clientes()
        
        # Crear ventas
        ventas = crear_ventas(clientes, productos, usuarios)
        
        print("=" * 60)
        print("✅ Seeder completado exitosamente!")
        print(f"📊 Resumen:")
        print(f"  🏢 Empresas: 1")
        print(f"  📁 Categorías: {Category.objects.count()}")
        print(f"  📦 Productos: {Product.objects.count()}")
        print(f"  👥 Clientes: {Client.objects.count()}")
        print(f"  👤 Usuarios: {User.objects.count()}")
        print(f"  💰 Ventas: {Sale.objects.count()}")
        print(f"  📋 Items de venta: {SaleItem.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error durante el seeding: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
