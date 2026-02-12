#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion_inicial.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

# Ejecutar dentro de: python manage.py shell
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.apps import apps

TipoUsuario = apps.get_model('members', 'TipoUsuario')
Usuarios = apps.get_model('members', 'Usuarios')

# mostrar campos del modelo Usuarios para diagnóstico
field_names = [f.name for f in Usuarios._meta.get_fields() if getattr(f, 'concrete', False)]
print("Campos concretos en Usuarios:", field_names)

# detectar nombre de la FK hacia TipoUsuario
fk_field = None
for f in Usuarios._meta.fields:
    if getattr(f, 'related_model', None) == TipoUsuario:
        fk_field = f.name
        break
print("Campo FK hacia TipoUsuario detectado:", fk_field)

# mapeo razonable de campos comunes (ajusta si tu modelo usa otros nombres)
candidates = {
    'nombres': ['nombres','nombre','first_name'],
    'apellido_paterno': ['apellido_paterno','apellido','last_name'],
    'correo': ['correo','email','mail'],
    'contrasena': ['contrasena','password'],
    'esta_activo': ['esta_activo','is_active'],
    'fecha_registro': ['fecha_registro','created_at','created']
}
field_map = {}
for key, opts in candidates.items():
    for o in opts:
        if o in field_names:
            field_map[key] = o
            break

print("Mapeo de campos detectado:", field_map)

# abortar si no detectamos al menos correo/contraseña/nombres
required = ['nombres','apellido_paterno','correo','contrasena']
if not all(k in field_map for k in required) or fk_field is None:
    print("\nNo se detectaron los campos necesarios automáticamente. Copia la lista de campos anterior y dime cómo se llaman.")
else:
    # crear roles por defecto
    roles = {}
    for name, desc in [
        ('Administrador','Acceso total'),
        ('Donador','Usuario que dona'),
        ('Beneficiario','Usuario que crea casos'),
        ('Intermediario','Usuario intermediario')
    ]:
        obj, created = TipoUsuario.objects.get_or_create(nombre=name, defaults={'descripcion': desc, 'fecha_creacion': timezone.now()})
        roles[name] = obj

    # helper para crear usuario con el mapeo dinámico
    def create_user(start_values):
        kwargs = {
            field_map['nombres']: start_values['nombres'],
            field_map['apellido_paterno']: start_values['apellido_paterno'],
            field_map['correo']: start_values['correo'],
            field_map['contrasena']: make_password(start_values['password']),
            'esta_activo': start_values.get('esta_activo', True) if 'esta_activo' in field_names else None,
            'fecha_registro': timezone.now() if 'fecha_registro' in field_names else None,
        }
        # limpiar claves None
        kwargs = {k:v for k,v in kwargs.items() if v is not None}
        # añadir FK a rol (usar el objeto TipoUsuario en el campo FK)
        kwargs[fk_field] = roles[start_values['rol']]
        return Usuarios.objects.create(**kwargs)

    # crear usuarios de prueba
    try:
        create_user({'nombres':'Admin','apellido_paterno':'Root','correo':'admin@example.test','password':'AdminPass123!','rol':'Administrador'})
        create_user({'nombres':'Carlos','apellido_paterno':'Donador','correo':'donador@example.test','password':'DonorPass123','rol':'Donador'})
        create_user({'nombres':'María','apellido_paterno':'Benef','correo':'beneficiario@example.test','password':'BenefPass123','rol':'Beneficiario'})
        create_user({'nombres':'Luisa','apellido_paterno':'Inter','correo':'intermediario@example.test','password':'InterPass123','rol':'Intermediario'})
        print("\nUsuarios creados correctamente. Credenciales de prueba:")
        print("admin@example.test / AdminPass123!")
        print("donador@example.test / DonorPass123")
        print("beneficiario@example.test / BenefPass123")
        print("intermediario@example.test / InterPass123")
    except Exception as e:
        print("Error al crear usuarios:", e)
