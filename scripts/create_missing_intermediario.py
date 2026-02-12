from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.apps import apps

TipoUsuario = apps.get_model('members', 'TipoUsuario')
Usuarios = apps.get_model('members', 'Usuarios')

# Asegurar rol Intermediario
role, _ = TipoUsuario.objects.get_or_create(
    nombre='Intermediario',
    defaults={'descripcion': 'Usuario intermediario', 'fecha_creacion': timezone.now()}
)

email = 'intermediario@example.test'
if Usuarios.objects.filter(correo=email).exists():
    print("El usuario intermediario ya existe:", email)
else:
    # detectar nombre real del campo FK hacia TipoUsuario
    fk_field = None
    for f in Usuarios._meta.fields:
        if getattr(f, 'related_model', None) == TipoUsuario:
            fk_field = f.name
            break
    if fk_field is None:
        # heurística común
        for candidate in ('id_tipo_usuario','idTipoUsuario','tipo_usuario','tipo','id_tipo','tipo_id'):
            if candidate in [f.name for f in Usuarios._meta.fields]:
                fk_field = candidate
                break

    if fk_field is None:
        raise SystemExit("No se pudo detectar el campo FK hacia TipoUsuario. Pega aquí la lista de campos de Usuarios y lo ajusto.")

    kwargs = {
        'nombres': 'Luisa',
        'apellido_paterno': 'Inter',
        'correo': email,
        'contrasena': make_password('InterPass123'),
        'fecha_registro': timezone.now(),
    }
    # añadir campos opcionales si existen
    field_names = [f.name for f in Usuarios._meta.get_fields() if getattr(f, 'concrete', False)]
    if 'esta_activo' in field_names:
        kwargs['esta_activo'] = True

    # asignar FK usando el nombre de campo detectado
    kwargs[fk_field] = role

    user = Usuarios.objects.create(**kwargs)
    print("Usuario creado:", getattr(user, 'correo', email), "contraseña: InterPass123")
