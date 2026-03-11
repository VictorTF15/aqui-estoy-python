import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aqui_estoy.settings')
django.setup()

from members.models import Usuarios, TipoUsuario
from django.contrib.auth.hashers import make_password

# Crear o obtener tipo de usuario Administrador
tipo_admin, _ = TipoUsuario.objects.get_or_create(
    nombre='Administrador',
    defaults={'descripcion': 'Usuario con permisos de administración'}
)

# Crear usuario administrador
admin = Usuarios.objects.create(
    nombres='Admin',
    apellido_paterno='Sistema',
    correo='admin@aquiestoy.com',
    contrasena=make_password('admin123'),
    telefono='1234567890',
    id_tipo_usuario=tipo_admin,
    ciudad='Puebla',
    estado='Puebla',
    esta_activo=True,
    is_staff=True,
    is_superuser=True
)

print(f"✅ Usuario administrador creado:")
print(f"   Correo: {admin.correo}")
print(f"   Contraseña: admin123")
print(f"   Tipo: {admin.id_tipo_usuario.nombre}")