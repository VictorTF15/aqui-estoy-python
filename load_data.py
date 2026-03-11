import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion_inicial.settings')
django.setup()

from members.models import *
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta

print("🗑️  Limpiando datos existentes...")
LogOCR.objects.all().delete()
DocumentosOCR.objects.all().delete()
Sanciones.objects.all().delete()
Reportes.objects.all().delete()
Mensajes.objects.all().delete()
Conversaciones.objects.all().delete()
Evidencias.objects.all().delete()
Donaciones.objects.all().delete()
CasoCategorias.objects.all().delete()
Casos.objects.all().delete()
Usuarios.objects.all().delete()
Categorias.objects.all().delete()
EstadoCaso.objects.all().delete()
TipoUsuario.objects.all().delete()
TipoMensaje.objects.all().delete()
EstadoReporte.objects.all().delete()
TipoSancion.objects.all().delete()
EstadoOCR.objects.all().delete()

print("✅ Datos limpiados")

# 1. TIPOS DE USUARIO
print("\n👥 Creando tipos de usuario...")
admin_tipo = TipoUsuario.objects.create(nombre='Administrador', descripcion='Usuario con acceso total al sistema')
donador_tipo = TipoUsuario.objects.create(nombre='Donador', descripcion='Usuario que realiza donaciones')
intermediario_tipo = TipoUsuario.objects.create(nombre='Intermediario', descripcion='Usuario que gestiona casos')
beneficiario_tipo = TipoUsuario.objects.create(nombre='Beneficiario', descripcion='Usuario que recibe donaciones')

# 2. CATEGORÍAS
print("📦 Creando categorías...")
cat_ropa = Categorias.objects.create(nombre='Ropa', descripcion='Prendas de vestir y accesorios')
cat_medicamento = Categorias.objects.create(nombre='Medicamento', descripcion='Medicinas y suministros médicos')
cat_comida = Categorias.objects.create(nombre='Comida', descripcion='Alimentos y bebidas')
cat_otros = Categorias.objects.create(nombre='Otros', descripcion='Artículos diversos')

# 3. ESTADOS DE CASO
print("📊 Creando estados de caso...")
est_pendiente = EstadoCaso.objects.create(nombre='Pendiente', descripcion='Caso creado, esperando revisión')
est_proceso = EstadoCaso.objects.create(nombre='En Proceso', descripcion='Caso en proceso de recaudación')
est_retrasado = EstadoCaso.objects.create(nombre='Retrasado', descripcion='Caso con retraso')
est_completado = EstadoCaso.objects.create(nombre='Completado', descripcion='Caso completado exitosamente')
est_cancelado = EstadoCaso.objects.create(nombre='Cancelado', descripcion='Caso cancelado')
est_urgente = EstadoCaso.objects.create(nombre='Urgente', descripcion='Caso urgente')

# 4. TIPOS DE MENSAJE
print("💬 Creando tipos de mensaje...")
tipo_texto = TipoMensaje.objects.create(nombre='Texto', descripcion='Mensaje de texto simple')
tipo_consulta = TipoMensaje.objects.create(nombre='Consulta', descripcion='Pregunta sobre un caso')
tipo_actualizacion = TipoMensaje.objects.create(nombre='Actualización', descripcion='Actualización de estado')
tipo_agradecimiento = TipoMensaje.objects.create(nombre='Agradecimiento', descripcion='Mensaje de agradecimiento')

# 5. ESTADOS DE REPORTE
print("🚨 Creando estados de reporte...")
EstadoReporte.objects.create(nombre='Pendiente', descripcion='Reporte pendiente')
EstadoReporte.objects.create(nombre='En Revisión', descripcion='Reporte en análisis')
EstadoReporte.objects.create(nombre='Resuelto', descripcion='Reporte resuelto')
EstadoReporte.objects.create(nombre='Rechazado', descripcion='Reporte rechazado')

# 6. TIPOS DE SANCIÓN
print("⚠️  Creando tipos de sanción...")
TipoSancion.objects.create(nombre='Advertencia', descripcion='Advertencia verbal', duracion_dias=0)
TipoSancion.objects.create(nombre='Suspensión Temporal', descripcion='Suspensión de 7 días', duracion_dias=7)
TipoSancion.objects.create(nombre='Suspensión Prolongada', descripcion='Suspensión de 30 días', duracion_dias=30)
TipoSancion.objects.create(nombre='Baneado Permanente', descripcion='Prohibición permanente', duracion_dias=0)

# 7. ESTADOS OCR
print("🔍 Creando estados OCR...")
EstadoOCR.objects.create(nombre='Pendiente', descripcion='Documento pendiente')
EstadoOCR.objects.create(nombre='Procesando', descripcion='Documento en proceso')
EstadoOCR.objects.create(nombre='Completado', descripcion='Documento procesado')
EstadoOCR.objects.create(nombre='Fallido', descripcion='Error en procesamiento')

# 8. USUARIOS
print("\n👤 Creando usuarios...")

# Administrador - NOMBRES DE CAMPOS CORREGIDOS
admin = Usuarios.objects.create(
    nombres='Juan Carlos',
    apellido_paterno='Pérez',
    apellido_materno='Rodríguez',
    correo='admin@gmail.com',
    contrasena=make_password('admin123'),
    telefono='5551234567',
    imagen_ine_frontal_url='INE_FRENTE_ADMIN.jpg',  # ✅ CORREGIDO
    imagen_ine_trasera_url='INE_TRASERA_ADMIN.jpg',  # ✅ CORREGIDO
    esta_activo=True,
    verificado=True,
    is_staff=True,
    is_superuser=True,
    id_tipo_usuario=admin_tipo
)
print(f"   ✓ Admin: {admin.correo}")

# Donadores
donadores = []
usuarios_donadores = [
    ('María Elena', 'González', 'López', 'maria.gonzalez@gmail.com', '5551234568'),
    ('Roberto', 'Martínez', 'Sánchez', 'roberto.martinez@gmail.com', '5551234569'),
    ('Carmen', 'Hernández', 'Torres', 'carmen.hernandez@gmail.com', '5551234570'),
]

for nombres, ap_pat, ap_mat, email, tel in usuarios_donadores:
    d = Usuarios.objects.create(
        nombres=nombres,
        apellido_paterno=ap_pat,
        apellido_materno=ap_mat,
        correo=email,
        contrasena=make_password('donador123'),
        telefono=tel,
        imagen_ine_frontal_url=f'INE_FRENTE_{nombres.upper()}.jpg',
        imagen_ine_trasera_url=f'INE_TRASERA_{nombres.upper()}.jpg',
        esta_activo=True,
        verificado=True,
        id_tipo_usuario=donador_tipo
    )
    donadores.append(d)
    print(f"   ✓ Donador: {d.correo}")

# Intermediarios
intermediarios = []
usuarios_intermediarios = [
    ('Luis Fernando', 'Ramírez', 'Morales', 'luis.ramirez@gmail.com', '5551234571'),
    ('Ana Patricia', 'Flores', 'Vega', 'ana.flores@gmail.com', '5551234572'),
]

for nombres, ap_pat, ap_mat, email, tel in usuarios_intermediarios:
    i = Usuarios.objects.create(
        nombres=nombres,
        apellido_paterno=ap_pat,
        apellido_materno=ap_mat,
        correo=email,
        contrasena=make_password('intermediario123'),
        telefono=tel,
        imagen_ine_frontal_url=f'INE_FRENTE_{nombres.split()[0].upper()}.jpg',
        imagen_ine_trasera_url=f'INE_TRASERA_{nombres.split()[0].upper()}.jpg',
        esta_activo=True,
        verificado=True,
        id_tipo_usuario=intermediario_tipo
    )
    intermediarios.append(i)
    print(f"   ✓ Intermediario: {i.correo}")

# Beneficiarios
beneficiarios = []
usuarios_beneficiarios = [
    ('Pedro', 'García', 'Ruiz', 'pedro.garcia@gmail.com', '5551234573'),
    ('Rosa María', 'López', 'Jiménez', 'rosa.lopez@gmail.com', '5551234574'),
    ('Miguel Ángel', 'Fernández', 'Castro', 'miguel.fernandez@gmail.com', '5551234575'),
    ('Patricia', 'Mendoza', 'Silva', 'patricia.mendoza@gmail.com', '5551234576'),
]

for nombres, ap_pat, ap_mat, email, tel in usuarios_beneficiarios:
    b = Usuarios.objects.create(
        nombres=nombres,
        apellido_paterno=ap_pat,
        apellido_materno=ap_mat,
        correo=email,
        contrasena=make_password('beneficiario123'),
        telefono=tel,
        imagen_ine_frontal_url=f'INE_FRENTE_{nombres.split()[0].upper()}.jpg',
        imagen_ine_trasera_url=f'INE_TRASERA_{nombres.split()[0].upper()}.jpg',
        esta_activo=True,
        verificado=True,
        id_tipo_usuario=beneficiario_tipo
    )
    beneficiarios.append(b)
    print(f"   ✓ Beneficiario: {b.correo}")

# 9. CASOS
print("\n📋 Creando casos...")
casos_data = [
    {
        'titulo': 'Familia necesita despensa urgente',
        'descripcion': 'Familia de 5 personas afectada por pérdida de empleo. Necesitan alimentos básicos urgentemente.',
        'colonia': 'Iztapalapa',
        'entidad': 'Ciudad de México',
        'latitud': 19.3571,
        'longitud': -99.0554,
        'prioridad': 5,
        'vistas': 45,
        'beneficiario': beneficiarios[0],
        'estado': est_urgente,
        'categoria': cat_comida,
        'dias_atras': 2
    },
    {
        'titulo': 'Ropa para niños de escuela primaria',
        'descripcion': 'Comunidad escolar necesita uniformes para 30 niños.',
        'colonia': 'Coyoacán',
        'entidad': 'Ciudad de México',
        'latitud': 19.3464,
        'longitud': -99.1614,
        'prioridad': 3,
        'vistas': 78,
        'beneficiario': beneficiarios[1],
        'estado': est_proceso,
        'categoria': cat_ropa,
        'dias_atras': 5
    },
    {
        'titulo': 'Medicamentos para adulto mayor con diabetes',
        'descripcion': 'Don José de 75 años necesita insulina.',
        'colonia': 'Tlalpan',
        'entidad': 'Ciudad de México',
        'latitud': 19.2840,
        'longitud': -99.1660,
        'prioridad': 4,
        'vistas': 92,
        'beneficiario': beneficiarios[2],
        'estado': est_retrasado,
        'categoria': cat_medicamento,
        'dias_atras': 10
    },
    {
        'titulo': 'Material escolar para inicio de clases',
        'descripcion': 'Escuela comunitaria necesita material para 50 alumnos.',
        'colonia': 'Xochimilco',
        'entidad': 'Ciudad de México',
        'latitud': 19.2569,
        'longitud': -99.1031,
        'prioridad': 2,
        'vistas': 34,
        'beneficiario': beneficiarios[3],
        'estado': est_pendiente,
        'categoria': cat_otros,
        'dias_atras': 1
    },
    {
        'titulo': 'Despensas para comunidad rural',
        'descripcion': 'Comunidad de 20 familias necesita alimentos.',
        'colonia': 'Tlajomulco de Zúñiga',
        'entidad': 'Jalisco',
        'latitud': 20.4736,
        'longitud': -103.4450,
        'prioridad': 3,
        'vistas': 56,
        'beneficiario': beneficiarios[0],
        'estado': est_proceso,
        'categoria': cat_comida,
        'dias_atras': 7
    },
    {
        'titulo': 'Medicamentos para niño con cáncer',
        'descripcion': 'Pequeño de 8 años con leucemia necesita quimioterapia.',
        'colonia': 'Monterrey',
        'entidad': 'Nuevo León',
        'latitud': 25.6866,
        'longitud': -100.3161,
        'prioridad': 5,
        'vistas': 150,
        'beneficiario': beneficiarios[1],
        'estado': est_urgente,
        'categoria': cat_medicamento,
        'dias_atras': 1
    },
    {
        'titulo': 'Ropa de invierno para albergue',
        'descripcion': 'Albergue recibió cobijas y ropa abrigadora.',
        'colonia': 'Puebla',
        'entidad': 'Puebla',
        'latitud': 19.0414,
        'longitud': -98.2063,
        'prioridad': 3,
        'vistas': 120,
        'beneficiario': beneficiarios[2],
        'estado': est_completado,
        'categoria': cat_ropa,
        'dias_atras': 15,
        'esta_abierto': False
    },
    {
        'titulo': 'Artículos de higiene para refugio temporal',
        'descripcion': 'Refugio necesita jabón, shampoo para 40 personas.',
        'colonia': 'Mérida',
        'entidad': 'Yucatán',
        'latitud': 20.9674,
        'longitud': -89.5926,
        'prioridad': 3,
        'vistas': 67,
        'beneficiario': beneficiarios[3],
        'estado': est_proceso,
        'categoria': cat_otros,
        'dias_atras': 4
    },
    {
        'titulo': 'Alimentos para comedores comunitarios',
        'descripcion': 'Red de 3 comedores solicita alimentos básicos.',
        'colonia': 'Tijuana',
        'entidad': 'Baja California',
        'latitud': 32.5149,
        'longitud': -117.0382,
        'prioridad': 4,
        'vistas': 89,
        'beneficiario': beneficiarios[0],
        'estado': est_pendiente,
        'categoria': cat_comida,
        'dias_atras': 3
    },
    {
        'titulo': 'Ropa para damnificados por inundación',
        'descripcion': 'Familias afectadas perdieron sus pertenencias.',
        'colonia': 'Villahermosa',
        'entidad': 'Tabasco',
        'latitud': 17.9969,
        'longitud': -92.9474,
        'prioridad': 5,
        'vistas': 210,
        'beneficiario': beneficiarios[1],
        'estado': est_urgente,
        'categoria': cat_ropa,
        'dias_atras': 0
    },
]

casos = []
for data in casos_data:
    caso = Casos.objects.create(
        titulo=data['titulo'],
        descripcion=data['descripcion'],
        colonia=data['colonia'],
        entidad=data['entidad'],
        latitud=data['latitud'],
        longitud=data['longitud'],
        esta_abierto=data.get('esta_abierto', True),
        prioridad=data['prioridad'],
        vistas=data['vistas'],
        id_beneficiario=data['beneficiario'],
        id_estado=data['estado'],
        fecha_creacion=timezone.now() - timedelta(days=data['dias_atras'])
    )
    
    # Asignar categoría
    CasoCategorias.objects.create(
        id_caso=caso,
        id_categoria=data['categoria']
    )
    
    casos.append(caso)
    print(f"   ✓ Caso: {caso.titulo[:50]}...")

# 10. DONACIONES
print("\n💰 Creando donaciones...")
Donaciones.objects.create(
    monto=500.00,
    estado_donacion='Completado',
    id_caso=casos[0],
    id_donador=donadores[0],
    fecha_compromiso=timezone.now() - timedelta(days=1),
    fecha_pago=timezone.now()
)

Donaciones.objects.create(
    monto=800.00,
    estado_donacion='Completado',
    id_caso=casos[1],
    id_donador=donadores[2],
    fecha_compromiso=timezone.now() - timedelta(days=3),
    fecha_pago=timezone.now() - timedelta(days=2)
)

Donaciones.objects.create(
    monto=2000.00,
    estado_donacion='Completado',
    id_caso=casos[5],
    id_donador=donadores[0],
    fecha_compromiso=timezone.now(),
    fecha_pago=timezone.now()
)

print("   ✓ 3 donaciones creadas")

# 11. EVIDENCIAS
print("\n📸 Creando evidencias...")
Evidencias.objects.create(
    titulo='Foto de la familia beneficiada',
    descripcion='Familia con despensa recibida',
    tipo_archivo='image',
    ruta_archivo='evidencias/caso1_familia.jpg',
    id_caso=casos[0],
    id_usuario=beneficiarios[0]
)

Evidencias.objects.create(
    titulo='Uniformes donados',
    descripcion='Foto de uniformes entregados',
    tipo_archivo='image',
    ruta_archivo='evidencias/caso2_uniformes.jpg',
    id_caso=casos[1],
    id_usuario=beneficiarios[1]
)

print("   ✓ 2 evidencias creadas")

# 12. CONVERSACIONES Y MENSAJES
print("\n💬 Creando conversaciones y mensajes...")
conv1 = Conversaciones.objects.create(
    id_usuario1=donadores[0],
    id_usuario2=beneficiarios[0],
    id_caso=casos[0],
    fecha_creacion=timezone.now() - timedelta(days=2)
)

Mensajes.objects.create(
    contenido='Hola, vi su caso y me gustaría ayudar',
    es_leido=True,
    id_conversacion=conv1,
    id_emisor=donadores[0],
    id_tipo=tipo_consulta,
    fecha_envio=timezone.now() - timedelta(days=2)
)

Mensajes.objects.create(
    contenido='Muchas gracias, realmente lo necesitamos',
    es_leido=True,
    id_conversacion=conv1,
    id_emisor=beneficiarios[0],
    id_tipo=tipo_agradecimiento,
    fecha_envio=timezone.now() - timedelta(days=2, hours=-1)
)

print("   ✓ 1 conversación con 2 mensajes creada")

print("\n" + "="*50)
print("✅ ¡DATOS DE PRUEBA CARGADOS EXITOSAMENTE!")
print("="*50)
print(f"\n📊 RESUMEN:")
print(f"   • Tipos de usuario: {TipoUsuario.objects.count()}")
print(f"   • Usuarios: {Usuarios.objects.count()}")
print(f"   • Categorías: {Categorias.objects.count()}")
print(f"   • Estados de caso: {EstadoCaso.objects.count()}")
print(f"   • Casos: {Casos.objects.count()}")
print(f"   • Donaciones: {Donaciones.objects.count()}")
print(f"   • Evidencias: {Evidencias.objects.count()}")
print(f"   • Conversaciones: {Conversaciones.objects.count()}")
print(f"   • Mensajes: {Mensajes.objects.count()}")

print("\n🔑 CREDENCIALES DE ACCESO:")
print("   • Admin: admin@gmail.com / admin123")
print("   • Donadores: [nombre]@gmail.com / donador123")
print("   • Intermediarios: [nombre]@gmail.com / intermediario123")
print("   • Beneficiarios: [nombre]@gmail.com / beneficiario123")