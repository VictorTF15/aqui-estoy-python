from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.apps import apps

TipoUsuario = apps.get_model('members', 'TipoUsuario')
Usuarios = apps.get_model('members', 'Usuarios')

# Mostrar campos para diagnóstico (si hace falta)
field_names = [f.name for f in Usuarios._meta.get_fields() if getattr(f, 'concrete', False)]
print("Campos concretos en Usuarios:", field_names)

# Detectar FK hacia TipoUsuario
fk_field = None
for f in Usuarios._meta.fields:
    if getattr(f, 'related_model', None) == TipoUsuario:
        fk_field = f.name
        break

# si no se detectó, buscar heurísticamente
if fk_field is None:
    for candidate in ('id_tipo_usuario','idTipoUsuario','tipo_usuario','tipo','id_tipo','tipo_id'):
        if candidate in field_names:
            fk_field = candidate
            break

print("Campo FK hacia TipoUsuario detectado:", fk_field)

# mapeo razonable de campos comunes
candidates = {
    'nombres': ['nombres','nombre','first_name','name'],
    'apellido_paterno': ['apellido_paterno','apellido','last_name','lastname','apellido1'],
    'correo': ['correo','email','mail'],
    'contrasena': ['contrasena','password','clave']
}
field_map = {}
for key, opts in candidates.items():
    for o in opts:
        if o in field_names:
            field_map[key] = o
            break

print("Mapeo de campos detectado:", field_map)

required = ['nombres','apellido_paterno','correo','contrasena']
if not all(k in field_map for k in required) or fk_field is None:
    print("\nNo se detectaron automáticamente todos los campos necesarios.")
    print("Si quieres, pega aquí la lista de campos que apareció arriba y adapto el script.")
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

    def create_or_get_user(data):
        lookup = { field_map['correo']: data['correo'] }
        defaults = {
            field_map['nombres']: data['nombres'],
            field_map['apellido_paterno']: data['apellido_paterno'],
            field_map['contrasena']: make_password(data['password']),
        }
        # añadir campos opcionales si existen
        if 'esta_activo' in field_names:
            defaults['esta_activo'] = data.get('esta_activo', True)
        if 'fecha_registro' in field_names:
            defaults['fecha_registro'] = timezone.now()
        # crear o recuperar
        user, created = Usuarios.objects.get_or_create(**lookup, defaults=defaults)
        # asignar rol FK si es necesario y no está asignado
        current = getattr(user, fk_field, None)
        if current is None or (hasattr(current, 'pk') and current.pk != roles[data['rol']].pk):
            setattr(user, fk_field, roles[data['rol']])
            user.save()
        return user, created

    samples = [
        {'nombres':'Admin','apellido_paterno':'Root','correo':'admin@example.test','password':'AdminPass123!','rol':'Administrador'},
        {'nombres':'Carlos','apellido_paterno':'Donador','correo':'donador@example.test','password':'DonorPass123','rol':'Donador'},
        {'nombres':'María','apellido_paterno':'Benef','correo':'beneficiario@example.test','password':'BenefPass123','rol':'Beneficiario'},
        {'nombres':'Luisa','apellido_paterno':'Inter','correo':'intermediario@example.test','password':'InterPass123','rol':'Intermediario'},
    ]

    for s in samples:
        try:
            u, created = create_or_get_user(s)
            print(f"Usuario {'creado' if created else 'existente'}: {getattr(u, field_map['correo'])} -> rol {getattr(getattr(u, fk_field), 'nombre', getattr(u, fk_field))}")
        except Exception as e:
            print("Error creando usuario", s['correo'], ":", e)

    print("\nCredenciales de prueba (login):")
    print("admin@example.test / AdminPass123!")
    print("donador@example.test / DonorPass123")
    print("beneficiario@example.test / BenefPass123")
    print("intermediario@example.test / InterPass123")