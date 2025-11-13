#!/usr/bin/env python
"""
Script para probar endpoints en el servidor de producción
"""
import requests
import sys

PRODUCTION_URL = 'https://24.144.94.118'
API_BASE = f'{PRODUCTION_URL}/api/v1'

def test_endpoint(path, method='GET', data=None, headers=None):
    """Probar un endpoint específico"""
    url = f'{API_BASE}{path}'
    print(f"\n🔍 Probando: {method} {url}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10, verify=False)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=10, verify=False)
        else:
            response = requests.request(method, url, json=data, headers=headers, timeout=10, verify=False)
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 404:
            print(f"   ❌ 404 Not Found - La ruta no existe")
        elif response.status_code == 200:
            print(f"   ✅ 200 OK - Funciona correctamente")
            try:
                print(f"   Response: {response.json()}")
            except:
                print(f"   Response: {response.text[:200]}")
        elif response.status_code == 301 or response.status_code == 302:
            print(f"   ⚠️  Redirect: {response.headers.get('Location', 'N/A')}")
        elif response.status_code == 403:
            print(f"   ⚠️  403 Forbidden - Necesita autenticación")
        elif response.status_code == 500:
            print(f"   ❌ 500 Error - Error del servidor")
            print(f"   Response: {response.text[:500]}")
        else:
            print(f"   ⚠️  Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
        return response
        
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL Error: {e}")
        print(f"   💡 Intenta con HTTP en lugar de HTTPS")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection Error: {e}")
        print(f"   💡 El servidor no está disponible o no responde")
        return None
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout - El servidor no respondió a tiempo")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    """Probar todos los endpoints"""
    print("=" * 60)
    print("🧪 PRUEBA DE ENDPOINTS EN PRODUCCIÓN")
    print("=" * 60)
    print(f"Servidor: {PRODUCTION_URL}")
    print(f"API Base: {API_BASE}")
    
    # Deshabilitar warnings de SSL si no hay certificado
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 1. Probar la raíz del servidor
    print("\n" + "=" * 60)
    print("1️⃣ Probando raíz del servidor")
    print("=" * 60)
    try:
        response = requests.get(PRODUCTION_URL, timeout=10, verify=False)
        print(f"✅ Servidor responde: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return
    
    # 2. Probar /api/v1/ directamente
    print("\n" + "=" * 60)
    print("2️⃣ Probando /api/v1/")
    print("=" * 60)
    test_endpoint('/')
    
    # 3. Probar endpoints de core (auth)
    print("\n" + "=" * 60)
    print("3️⃣ Probando endpoints de autenticación")
    print("=" * 60)
    test_endpoint('/auth/login/', 'POST', {'username': 'admin', 'password': 'test'})
    
    # 4. Probar endpoints de mobile
    print("\n" + "=" * 60)
    print("4️⃣ Probando endpoints móviles")
    print("=" * 60)
    test_endpoint('/mobile/products/dashboard/')
    test_endpoint('/mobile/notifications/register-device/', 'POST', {
        'device_token': 'ExponentPushToken[test]',
        'device_type': 'android'
    })
    
    # 5. Probar otros endpoints comunes
    print("\n" + "=" * 60)
    print("5️⃣ Probando otros endpoints")
    print("=" * 60)
    test_endpoint('/products/')
    test_endpoint('/sales/')
    test_endpoint('/notifications/notifications/')
    
    # 6. Probar admin
    print("\n" + "=" * 60)
    print("6️⃣ Probando admin")
    print("=" * 60)
    try:
        response = requests.get(f'{PRODUCTION_URL}/admin/', timeout=10, verify=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Admin accesible")
        elif response.status_code == 302:
            print(f"   ✅ Admin redirige (normal)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 7. Intentar con HTTP si HTTPS falla
    print("\n" + "=" * 60)
    print("7️⃣ Probando con HTTP (sin SSL)")
    print("=" * 60)
    http_url = PRODUCTION_URL.replace('https://', 'http://')
    http_api = f'{http_url}/api/v1'
    try:
        response = requests.get(f'{http_api}/', timeout=10)
        print(f"   ✅ HTTP funciona: {response.status_code}")
    except Exception as e:
        print(f"   ❌ HTTP también falla: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("=" * 60)
    
    print("\n💡 DIAGNÓSTICO:")
    print("   Si todos los endpoints dan 404:")
    print("   1. Verifica que el servidor web (nginx/apache) esté configurado")
    print("   2. Verifica que Django esté corriendo")
    print("   3. Verifica que ALLOWED_HOSTS incluya la IP")
    print("   4. Verifica la configuración de proxy_pass en nginx")
    print("   5. Verifica que SECURE_SSL_REDIRECT esté correcto")

if __name__ == '__main__':
    main()

