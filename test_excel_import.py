#!/usr/bin/env python
"""
Script para probar la importación de productos desde Excel
Incluye verificación antes y después de la importación
"""
import os
import sys
import django
import requests
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

def get_products_list():
    """Obtener lista de productos con sus stocks"""
    products = Product.objects.all().order_by('sku')
    print(f"\n📦 PRODUCTOS ACTUALES ({products.count()} total):")
    print("=" * 80)
    for product in products:
        print(f"  SKU: {product.sku:20} | Nombre: {product.name[:30]:30} | Stock: {product.stock:5}")
    print("=" * 80)
    return products

def test_excel_import(excel_file_path):
    """Probar importación de Excel"""
    
    print("🧪 PRUEBA DE IMPORTACIÓN DE PRODUCTOS DESDE EXCEL")
    print("=" * 80)
    
    # 1. Obtener usuario admin para autenticación
    try:
        admin = User.objects.filter(is_staff=True).first()
        if not admin:
            print("❌ No hay usuarios admin")
            return False
        
        print(f"✅ Usuario admin: {admin.username}")
        
        # Obtener token de autenticación
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(admin)
        token = str(refresh.access_token)
        print(f"✅ Token obtenido")
        
    except Exception as e:
        print(f"❌ Error obteniendo usuario/token: {e}")
        return False
    
    # 2. Listar productos ANTES de importar
    print("\n" + "=" * 80)
    print("📋 ANTES DE IMPORTAR:")
    print("=" * 80)
    products_before = get_products_list()
    
    # Guardar stocks antes para comparación
    stocks_before = {p.sku: p.stock for p in products_before}
    
    # 3. Importar archivo Excel
    print("\n" + "=" * 80)
    print("📤 IMPORTANDO ARCHIVO EXCEL...")
    print("=" * 80)
    print(f"Archivo: {excel_file_path}")
    
    if not os.path.exists(excel_file_path):
        print(f"❌ El archivo no existe: {excel_file_path}")
        return False
    
    try:
        url = 'http://localhost:8000/api/v1/mobile/products/import-excel/'
        headers = {
            'Authorization': f'Bearer {token}',
        }
        
        with open(excel_file_path, 'rb') as f:
            files = {'file': (os.path.basename(excel_file_path), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print("📡 Enviando request al servidor...")
            response = requests.post(url, files=files, headers=headers, timeout=60)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Importación completada:")
                print(f"   Total filas: {result.get('total_rows', 0)}")
                print(f"   Exitosas: {result.get('successful', 0)}")
                print(f"   Fallidas: {result.get('failed', 0)}")
                
                if result.get('errors'):
                    print(f"\n⚠️  Errores encontrados ({len(result['errors'])}):")
                    for error in result['errors'][:10]:
                        print(f"   - {error}")
            else:
                print(f"❌ Error en la importación:")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error al importar: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. Listar productos DESPUÉS de importar
    print("\n" + "=" * 80)
    print("📋 DESPUÉS DE IMPORTAR:")
    print("=" * 80)
    
    # Refrescar desde BD
    products_after = Product.objects.all().order_by('sku')
    
    print(f"\n📦 PRODUCTOS DESPUÉS ({products_after.count()} total):")
    print("=" * 80)
    
    changes_found = False
    for product in products_after:
        stock_before = stocks_before.get(product.sku, 0)
        stock_after = product.stock
        change = stock_after - stock_before
        
        if change != 0 or product.sku not in stocks_before:
            changes_found = True
            status = "🆕 NUEVO" if product.sku not in stocks_before else "🔄 ACTUALIZADO"
            print(f"  {status} | SKU: {product.sku:20} | Stock: {stock_before:5} → {stock_after:5} (Δ{change:+5}) | {product.name[:30]}")
        else:
            print(f"  ➖ Sin cambios | SKU: {product.sku:20} | Stock: {stock_after:5} | {product.name[:30]}")
    
    print("=" * 80)
    
    # 5. Resumen de cambios
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE CAMBIOS:")
    print("=" * 80)
    
    new_products = [p for p in products_after if p.sku not in stocks_before]
    updated_products = [p for p in products_after if p.sku in stocks_before and p.stock != stocks_before[p.sku]]
    
    print(f"🆕 Productos nuevos: {len(new_products)}")
    for p in new_products:
        print(f"   - {p.sku}: {p.name} (Stock: {p.stock})")
    
    print(f"\n🔄 Productos actualizados: {len(updated_products)}")
    for p in updated_products:
        change = p.stock - stocks_before[p.sku]
        print(f"   - {p.sku}: {p.name}")
        print(f"     Stock: {stocks_before[p.sku]} → {p.stock} (Δ{change:+})")
    
    unchanged = [p for p in products_after if p.sku in stocks_before and p.stock == stocks_before[p.sku]]
    print(f"\n➖ Sin cambios: {len(unchanged)}")
    
    if not new_products and not updated_products:
        print("\n⚠️  ADVERTENCIA: No se encontraron cambios. Revisa:")
        print("   1. Que el archivo Excel tenga productos con SKU válidos")
        print("   2. Que los SKUs en el Excel existan o sean nuevos")
        print("   3. Los logs del servidor Django")
    
    print("\n" + "=" * 80)
    print("✅ Prueba completada")
    
    return True

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python test_excel_import.py <ruta_al_archivo_excel.xlsx>")
        print("\nEjemplo:")
        print("  python test_excel_import.py productos_template.xlsx")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    test_excel_import(excel_file)

