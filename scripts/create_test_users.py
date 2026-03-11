import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion_inicial.settings')
django.setup()

from members.models import Usuarios, TipoUsuario
from django.utils import timezone

def create_test_users():
    # Crear tipos de usuario
    tipos = {
        'Administrador': 'Usuario con permisos completos del sistema',
        'Donador': 'Usuario que realiza donaciones',
        'Beneficiario': 'Usuario que recibe donaciones',
        'Intermediario': 'Usuario que coordina donaciones'
    }
    
    for nombre, descripcion in tipos.items():
        TipoUsuario.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion, 'fecha_creacion': timezone.now()}
        )
    
    # Crear usuarios de prueba
    usuarios_prueba = [
        {
            'correo': 'admin@example.test',
            'nombres': 'Admin',
            'apellido_paterno': 'Sistema',
            'tipo': 'Administrador',
            'password': 'AdminPass123!',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'correo': 'donador@example.test',
            'nombres': 'Juan',
            'apellido_paterno': 'Donador',
            'tipo': 'Donador',
            'password': 'DonorPass123'
        },
        {
            'correo': 'beneficiario@example.test',
            'nombres': 'María',
            'apellido_paterno': 'Beneficiaria',
            'tipo': 'Beneficiario',
            'password': 'BenefPass123'
        },
        {
            'correo': 'intermediario@example.test',
            'nombres': 'Carlos',
            'apellido_paterno': 'Intermediario',
            'tipo': 'Intermediario',
            'password': 'InterPass123'
        }
    ]
    
    for user_data in usuarios_prueba:
        tipo = TipoUsuario.objects.get(nombre=user_data['tipo'])
        
        if not Usuarios.objects.filter(correo=user_data['correo']).exists():
            user = Usuarios.objects.create_user(
                correo=user_data['correo'],
                nombres=user_data['nombres'],
                apellido_paterno=user_data['apellido_paterno'],
                password=user_data['password'],
                id_tipo_usuario=tipo,
                is_staff=user_data.get('is_staff', False),
                is_superuser=user_data.get('is_superuser', False)
            )
            print(f"✓ Usuario creado: {user.correo} ({user_data['tipo']})")
        else:
            print(f"- Usuario ya existe: {user_data['correo']}")

if __name__ == '__main__':
    create_test_users()
    print("\n¡Usuarios de prueba creados exitosamente!")