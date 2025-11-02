#!/usr/bin/env python
"""
Script para verificar y crear usuarios necesarios en PostgreSQL
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.core.models import User

def verify_and_create_users():
    """Verificar y crear usuarios necesarios"""
    print("👥 Verificando y creando usuarios necesarios...")
    print("=" * 60)
    
    # Usuarios que deberían existir según los scripts de seed
    usuarios_data = [
        {
            'username': 'admin',
            'email': 'admin@smartsales365.com',
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'is_staff': True,
            'is_superuser': True,
            'password': 'admin123'  # Cambiar si es necesario
        },
        {
            'username': 'gerente',
            'email': 'gerente@smartsales365.com',
            'first_name': 'María',
            'last_name': 'González',
            'is_staff': True,
            'is_superuser': False,
            'password': 'password123'
        },
        {
            'username': 'vendedor1',
            'email': 'vendedor1@smartsales365.com',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'is_staff': False,
            'is_superuser': False,
            'password': 'password123'
        },
        {
            'username': 'vendedor2',
            'email': 'vendedor2@smartsales365.com',
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'is_staff': False,
            'is_superuser': False,
            'password': 'password123'
        },
        {
            'username': 'cajero1',
            'email': 'cajero1@smartsales365.com',
            'first_name': 'Luis',
            'last_name': 'Hernández',
            'is_staff': False,
            'is_superuser': False,
            'password': 'password123'
        }
    ]
    
    usuarios_creados = []
    usuarios_existentes = []
    
    for user_data in usuarios_data:
        password = user_data.pop('password')
        
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                **user_data,
                'is_active': True
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            usuarios_creados.append(user)
            status = "🟢 CREADO"
        else:
            # Actualizar si es necesario (solo campos no críticos)
            updated = False
            if user.email != user_data['email']:
                user.email = user_data['email']
                updated = True
            if user.first_name != user_data['first_name']:
                user.first_name = user_data['first_name']
                updated = True
            if user.last_name != user_data['last_name']:
                user.last_name = user_data['last_name']
                updated = True
            if user.is_staff != user_data['is_staff']:
                user.is_staff = user_data['is_staff']
                updated = True
            if user.is_superuser != user_data['is_superuser']:
                user.is_superuser = user_data['is_superuser']
                updated = True
            
            if updated:
                user.save()
                status = "🟡 ACTUALIZADO"
            else:
                status = "✅ EXISTE"
            
            usuarios_existentes.append(user)
        
        roles = []
        if user.is_superuser:
            roles.append("Superadmin")
        if user.is_staff:
            roles.append("Admin")
        if not roles:
            roles.append("Usuario")
        
        print(f"{status} - {user.username}")
        print(f"      Email: {user.email}")
        print(f"      Nombre: {user.first_name} {user.last_name}")
        print(f"      Roles: {', '.join(roles)}")
        print()
    
    print("=" * 60)
    print(f"✅ Total usuarios: {User.objects.count()}")
    print(f"   - Creados ahora: {len(usuarios_creados)}")
    print(f"   - Ya existían: {len(usuarios_existentes)}")
    print("\n📋 Credenciales:")
    print("   admin / admin123 (Superadmin)")
    print("   gerente / password123 (Admin)")
    print("   vendedor1 / password123")
    print("   vendedor2 / password123")
    print("   cajero1 / password123")
    
    return usuarios_creados + usuarios_existentes

if __name__ == '__main__':
    verify_and_create_users()

