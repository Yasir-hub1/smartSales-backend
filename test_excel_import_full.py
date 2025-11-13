#!/usr/bin/env python
"""
Script completo para probar importación de Excel:
1. Lista productos antes
2. Importa el Excel
3. Lista productos después
4. Compara cambios
"""
import os
import sys
import django
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.products.models import Product
from django.contrib.auth import get_user_model
import json

User = get_user_model()

def get_products_via_api(token):
    """Obtener productos desde la API"""
    try:
        url = 'http://localhost:8000/api/v1/mobile/products/dashboard/'
        headers = {'Authorization': f'Bearer {token}'}
        params = {'page_size': 1000}  # Obtener todos
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            print(f"❌ Error API: {response.status_code}")
            print(response.text)
            return []
    except Exception as e:
        print(f"❌ Error obteniendo productos via API: {e}")
        return []

def get_products_from_db():
    """Obtener productos directamente de la BD"""
    products = Product.objects.all().order_by('sku')
    return {p.sku: {'id': p.id, 'name': p.name, 'stock': p.stock} for p in products}

def print_products_list(products_dict, title="PRODUCTOS"):
    """Imprimir lista de productos"""
    print(f"\n📦 {title} ({len(products_dict)} total):")
    print("=" * 80)
    for sku, info in sorted(products_dict.items()):
        print(f"  SKU: {sku:20} | Stock: {info['stock']:5} | {info['name'][:40]}")
    print("=" * 80)

def test_import_with_file(excel_file_path):
    """Probar importación completa"""
    
    print("🧪 PRUEBA COMPLETA DE IMPORTACIÓN DE EXCEL")
    print("=" * 80)
    
    # 1. Obtener usuario y token
    try:
        admin = User.objects.filter(is_staff=True).first()
        if not admin:
            print("❌ No hay usuarios admin")
            return False
        
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(admin)
        token = str(refresh.access_token)
        print(f"✅ Usuario: {admin.username}")
        print(f"✅ Token obtenido")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 2. Obtener productos ANTES (desde BD directamente)
    print("\n" + "=" * 80)
    print("1️⃣ PRODUCTOS ANTES DE IMPORTAR (desde BD):")
    print("=" * 80)
    products_before_db = get_products_from_db()
    print_products_list(products_before_db)
    
    # 3. Obtener productos ANTES (desde API)
    print("\n" + "=" * 80)
    print("2️⃣ PRODUCTOS ANTES DE IMPORTAR (desde API):")
    print("=" * 80)
    products_before_api = get_products_via_api(token)
    if products_before_api:
        api_dict = {p['sku']: {'name': p['name'], 'stock': p['stock']} for p in products_before_api}
        print_products_list(api_dict, "PRODUCTOS VÍA API")
    else:
        print("⚠️  No se pudieron obtener productos desde la API")
    
    # 4. Importar Excel
    print("\n" + "=" * 80)
    print("3️⃣ IMPORTANDO ARCHIVO EXCEL...")
    print("=" * 80)
    
    if not os.path.exists(excel_file_path):
        print(f"❌ Archivo no existe: {excel_file_path}")
        return False
    
    try:
        url = 'http://localhost:8000/api/v1/mobile/products/import-excel/'
        headers = {'Authorization': f'Bearer {token}'}
        
        with open(excel_file_path, 'rb') as f:
            files = {'file': (os.path.basename(excel_file_path), f, 
                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print(f"📤 Enviando: {excel_file_path}")
            response = requests.post(url, files=files, headers=headers, timeout=120)
            
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Resultado:")
                print(f"   Total filas procesadas: {result.get('total_rows', 0)}")
                print(f"   ✅ Exitosas: {result.get('successful', 0)}")
                print(f"   ❌ Fallidas: {result.get('failed', 0)}")
                
                if result.get('errors'):
                    print(f"\n⚠️  Errores ({len(result['errors'])}):")
                    for error in result['errors'][:10]:
                        print(f"   - {error}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"❌ Error importando: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Obtener productos DESPUÉS (desde BD directamente)
    print("\n" + "=" * 80)
    print("4️⃣ PRODUCTOS DESPUÉS DE IMPORTAR (desde BD):")
    print("=" * 80)
    products_after_db = get_products_from_db()
    print_products_list(products_after_db)
    
    # 6. Comparar cambios
    print("\n" + "=" * 80)
    print("5️⃣ ANÁLISIS DE CAMBIOS:")
    print("=" * 80)
    
    new_products = []
    updated_products = []
    unchanged_products = []
    
    for sku, info_after in products_after_db.items():
        if sku not in products_before_db:
            new_products.append((sku, info_after))
        else:
            stock_before = products_before_db[sku]['stock']
            stock_after = info_after['stock']
            if stock_before != stock_after:
                updated_products.append((sku, products_before_db[sku], info_after))
            else:
                unchanged_products.append((sku, info_after))
    
    print(f"\n🆕 Productos NUEVOS: {len(new_products)}")
    for sku, info in new_products:
        print(f"   + {sku:20} | Stock: {info['stock']:5} | {info['name'][:40]}")
    
    print(f"\n🔄 Productos ACTUALIZADOS: {len(updated_products)}")
    for sku, info_before, info_after in updated_products:
        change = info_after['stock'] - info_before['stock']
        print(f"   ↻ {sku:20} | {info_before['stock']:5} → {info_after['stock']:5} (Δ{change:+5}) | {info_after['name'][:40]}")
    
    print(f"\n➖ Sin cambios: {len(unchanged_products)}")
    
    # 7. Verificar desde API
    print("\n" + "=" * 80)
    print("6️⃣ PRODUCTOS DESPUÉS (desde API):")
    print("=" * 80)
    products_after_api = get_products_via_api(token)
    if products_after_api:
        api_dict = {p['sku']: {'name': p['name'], 'stock': p['stock']} for p in products_after_api}
        print_products_list(api_dict, "PRODUCTOS VÍA API")
    else:
        print("⚠️  No se pudieron obtener productos desde la API")
    
    # 8. Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL:")
    print("=" * 80)
    print(f"   Productos antes: {len(products_before_db)}")
    print(f"   Productos después: {len(products_after_db)}")
    print(f"   Nuevos: {len(new_products)}")
    print(f"   Actualizados: {len(updated_products)}")
    
    if len(new_products) == 0 and len(updated_products) == 0:
        print("\n⚠️  ⚠️  ⚠️  ADVERTENCIA CRÍTICA ⚠️  ⚠️  ⚠️")
        print("   NO SE ENCONTRARON CAMBIOS!")
        print("   Esto puede indicar:")
        print("   1. El archivo Excel no tiene productos válidos")
        print("   2. Los SKUs en el Excel no coinciden con productos existentes")
        print("   3. Hay un problema con la lógica de actualización")
        print("   4. Revisa los logs del servidor Django")
    
    print("\n" + "=" * 80)
    return True

if __name__ == '__main__':
    excel_file = "./productos_template_1762027427329 (1).xlsx"
    
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    
    if not os.path.exists(excel_file):
        print(f"❌ Archivo no encontrado: {excel_file}")
        print("\nArchivos Excel disponibles:")
        import glob
        for f in glob.glob("*.xlsx"):
            print(f"  - {f}")
        sys.exit(1)
    
    test_import_with_file(excel_file)

