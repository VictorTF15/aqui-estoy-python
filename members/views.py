from django.apps import apps
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.template.loader import select_template
from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from django.db.models import Sum, Count, Q

from .models import Usuarios, Casos, Donaciones, CasoCategorias, Categorias, EstadoCaso, TipoUsuario
from .decorators import login_required_session, role_required, anonymous_required

# resolución segura de modelos
def _get_model(name):
    try:
        return apps.get_model('members', name)
    except Exception:
        return None

Usuarios = _get_model('Usuarios')
Casos = _get_model('Casos')
Donaciones = _get_model('Donaciones')
Categorias = _get_model('Categorias')
EstadoCaso = _get_model('EstadoCaso')
TipoUsuario = _get_model('TipoUsuario')

@login_required_session
def feed(request):
    """Feed personalizado según el rol del usuario"""
    user_id = request.session.get('user_id')
    role = request.session.get('user_role', '')
    
    context = {
        'role': role,
        'recientes': [],
        'categorias': [],
        'usuario': None,
        'stats': {},
    }
    
    # Obtener datos del usuario
    if Usuarios and user_id:
        try:
            usuario = Usuarios.objects.get(pk=user_id)
            context['usuario'] = usuario
        except Usuarios.DoesNotExist:
            pass
    
    # Categorías para sidebar
    if Categorias:
        context['categorias'] = Categorias.objects.all()[:10]
    
    # Contenido según el rol
    if role == 'Beneficiario':
        # Vista para beneficiarios: sus casos y estadísticas personales
        if Casos and user_id:
            # CORREGIR: usar id_beneficiario en lugar de id_usuario
            mis_casos = Casos.objects.filter(id_beneficiario=user_id).select_related('id_estado').order_by('-fecha_creacion')
            context['mis_casos'] = mis_casos[:5]
            
            # Estadísticas personales del beneficiario
            total_recaudado = 0
            if Donaciones:
                # CORREGIR: usar id_beneficiario en lugar de id_usuario
                total_recaudado = Donaciones.objects.filter(
                    id_caso__id_beneficiario=user_id
                ).aggregate(total=Sum('monto'))['total'] or 0
            
            context['stats'] = {
                'mis_casos_total': mis_casos.count(),
                'mis_casos_activos': mis_casos.filter(id_estado__nombre='Activo').count(),
                'total_recaudado': total_recaudado,
            }
            
            # Casos recientes propios
            context['recientes'] = mis_casos[:5]
    
    elif role == 'Donador':
        # Vista para donadores: sus donaciones y casos sugeridos
        if Donaciones and user_id:
            mis_donaciones = Donaciones.objects.filter(
                id_donador=user_id
            ).select_related('id_caso').order_by('-fecha_compromiso')
            context['mis_donaciones'] = mis_donaciones[:5]
            
            # Estadísticas personales del donador
            total_donado = mis_donaciones.aggregate(total=Sum('monto'))['total'] or 0
            casos_apoyados = mis_donaciones.values('id_caso').distinct().count()
            
            context['stats'] = {
                'total_donado': total_donado,
                'casos_apoyados': casos_apoyados,
                'donaciones_realizadas': mis_donaciones.count(),
            }
        
        # Casos recientes que puede apoyar
        if Casos:
            # CORREGIR: usar id_beneficiario en lugar de id_usuario
            context['recientes'] = Casos.objects.filter(
                id_estado__nombre='Activo'
            ).exclude(
                id_beneficiario=user_id
            ).select_related('id_estado', 'id_beneficiario').order_by('-fecha_creacion')[:5]
    
    elif role == 'Administrador':
        # Vista administrativa: estadísticas globales
        stats = {}
        
        if Casos:
            stats['total_casos'] = Casos.objects.count()
            stats['casos_activos'] = Casos.objects.filter(id_estado__nombre='Activo').count()
            stats['casos_completados'] = Casos.objects.filter(id_estado__nombre='Completado').count()
        
        if Usuarios:
            stats['total_usuarios'] = Usuarios.objects.count()
            stats['usuarios_activos'] = Usuarios.objects.filter(esta_activo=True).count()
            stats['beneficiarios'] = Usuarios.objects.filter(id_tipo_usuario__nombre='Beneficiario').count()
            stats['donadores'] = Usuarios.objects.filter(id_tipo_usuario__nombre='Donador').count()
        
        if Donaciones:
            stats['total_donaciones_count'] = Donaciones.objects.count()
            stats['total_donado'] = Donaciones.objects.aggregate(total=Sum('monto'))['total'] or 0
        
        context['stats'] = stats
        
        # Casos recientes globales
        # CORREGIR: usar id_beneficiario en lugar de id_usuario
        if Casos:
            context['recientes'] = Casos.objects.select_related('id_estado', 'id_beneficiario').order_by('-fecha_creacion')[:5]
    
    else:
        # Vista por defecto para otros roles
        if Casos:
            context['recientes'] = Casos.objects.select_related('id_estado').order_by('-fecha_creacion')[:5]
    
    return render(request, 'members/feed.html', context)


@anonymous_required
def login_view(request):
    """Login de usuarios - solo accesible sin sesión"""
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        contrasena = request.POST.get('contrasena', '')
        
        if Usuarios:
            try:
                usuario = Usuarios.objects.filter(correo=correo).first()
                if usuario:
                    raw_pass = getattr(usuario, 'contrasena', '') or getattr(usuario, 'password', '')
                    ok = False
                    try:
                        ok = check_password(contrasena, raw_pass)
                    except Exception:
                        ok = (contrasena == raw_pass)
                    
                    if ok:
                        # Verificar si está activo
                        if not usuario.esta_activo:
                            messages.error(request, "Tu cuenta está desactivada. Contacta al administrador.")
                            return render(request, 'members/login.html')
                        
                        request.session['user_id'] = usuario.id
                        request.session['user_name'] = f"{getattr(usuario,'nombres','')} {getattr(usuario,'apellido_paterno','')}".strip()
                        
                        # Extraer rol
                        role = ''
                        for attr in ('id_tipo_usuario', 'idTipoUsuario', 'tipo_usuario', 'rol', 'role'):
                            val = getattr(usuario, attr, None)
                            if val:
                                role = getattr(val, 'nombre', str(val))
                                break
                        request.session['user_role'] = role
                        
                        messages.success(request, f"¡Bienvenido {usuario.nombres}!")
                        return redirect('members:feed')
            except Exception as e:
                messages.error(request, f"Error al iniciar sesión: {str(e)}")
        
        messages.error(request, "Credenciales inválidas.")
    
    return render(request, 'members/login.html')


@anonymous_required
def register(request):
    """Registro de nuevos usuarios - solo accesible sin sesión"""
    Usuarios = None
    try:
        Usuarios = apps.get_model('members', 'Usuarios')
    except Exception:
        Usuarios = None

    if request.method == "POST":
        correo = request.POST.get('correo', '').strip()
        nombres = request.POST.get('nombres', '').strip()
        contrasena = request.POST.get('contrasena', '')
        if Usuarios:
            try:
                # ajusta campos según tu modelo real si hace falta
                Usuarios.objects.create(correo=correo, nombres=nombres, contrasena=contrasena)
                messages.success(request, "Usuario creado correctamente.")
                return redirect('members:login')
            except Exception:
                messages.error(request, "Error al crear usuario en la base de datos.")
        else:
            # fallback: no hay modelo, simular registro
            messages.info(request, "Registro simulado (modelo Usuarios no encontrado).")
            return redirect('members:login')

    return render(request, 'members/register.html')


def logout_view(request):
    """Cerrar sesión del usuario"""
    # Obtener nombre antes de limpiar sesión
    user_name = request.session.get('user_name', 'Usuario')
    
    # Limpiar toda la sesión
    request.session.flush()
    
    messages.success(request, f"Hasta pronto, {user_name}. Has cerrado sesión exitosamente.")
    return redirect('members:login')


@login_required_session
@role_required('Administrador')
def lista_usuarios(request):
    """Lista de usuarios - solo para administradores"""
    if not Usuarios:
        return render(request, 'members/lista_usuarios.html', {'usuarios': [], 'tipos_usuario': []})
    
    usuarios = Usuarios.objects.select_related('id_tipo_usuario').order_by('-fecha_registro')
    tipos_usuario = TipoUsuario.objects.all() if TipoUsuario else []
    
    return render(request, 'members/lista_usuarios.html', {
        'usuarios': usuarios,
        'tipos_usuario': tipos_usuario
    })


@login_required_session
@role_required('Administrador')
def crear_usuario_modal(request):
    """Crear/editar usuario - solo para administradores"""
    # ...existing code...


@login_required_session
@role_required('Administrador')
def eliminar_usuario(request, user_id):
    """Eliminar usuario - solo para administradores"""
    # ...existing code...


@login_required_session
@role_required('Beneficiario', 'Administrador')
def crear_caso(request):
    """Crear caso - solo beneficiarios y administradores"""
    # ...existing code...


@login_required_session
def lista_casos(request):
    """Lista de casos - accesible para usuarios autenticados"""
    if not Casos:
        return render(request, 'members/lista_casos.html', {'casos': []})
    
    casos = Casos.objects.select_related('id_beneficiario', 'id_estado').order_by('-fecha_creacion')
    
    # Filtro por categoría si viene en query params
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        try:
            casos = casos.filter(casocategorias__id_categoria_id=categoria_id)
        except Exception:
            pass
    
    return render(request, 'members/lista_casos.html', {'casos': casos})


@login_required_session
def detalle_caso(request, caso_id):
    """Detalle de caso - accesible para usuarios autenticados"""
    if not Casos:
        return render(request, 'members/detalle_caso.html', {'caso': None})
    caso = get_object_or_404(Casos, pk=caso_id)
    return render(request, 'members/detalle_caso.html', {'caso': caso})


@login_required_session
@role_required('Donador', 'Administrador')
def crear_donacion(request, caso_id):
    """Crear donación - solo donadores y administradores"""
    if not (Donaciones and Casos and Usuarios):
        messages.error(request, "Modelos no disponibles.")
        return redirect('members:lista_casos')
    
    caso = get_object_or_404(Casos, pk=caso_id)
    user_id = request.session.get('user_id')
    
    if request.method == 'POST':
        monto_str = request.POST.get('monto', '0').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        try:
            monto = float(monto_str)
            if monto <= 0:
                messages.error(request, "El monto debe ser mayor a cero.")
                return render(request, 'members/crear_donacion.html', {'caso': caso})
            
            donador = Usuarios.objects.get(pk=user_id)
            
            donacion = Donaciones.objects.create(
                id_caso=caso,
                id_donador=donador,
                monto=monto,
                descripcion_donacion=descripcion,
                estado_donacion='Pendiente',
            )
            
            messages.success(request, f"¡Donación de ${monto} registrada exitosamente!")
            return redirect('members:detalle_caso', caso_id=caso.id)
            
        except ValueError:
            messages.error(request, "Monto inválido.")
        except Usuarios.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect('members:login')
        except Exception as e:
            messages.error(request, f"Error al crear donación: {str(e)}")
    
    return render(request, 'members/crear_donacion.html', {'caso': caso})


@login_required_session
def perfil_usuario(request, user_id):
    """Ver perfil de usuario - accesible para usuarios autenticados"""
    if not Usuarios:
        return render(request, 'members/perfil_usuario.html', {'usuario': None})
    
    usuario = get_object_or_404(Usuarios, pk=user_id)
    
    # Obtener casos del usuario como beneficiario
    casos_beneficiario = Casos.objects.filter(id_beneficiario=usuario).select_related('id_estado').order_by('-fecha_creacion') if Casos else []
    
    # Obtener donaciones realizadas por el usuario
    donaciones_realizadas = Donaciones.objects.filter(id_donador=usuario).select_related('id_caso').order_by('-fecha_compromiso') if Donaciones else []
    
    # Estadísticas
    total_casos = casos_beneficiario.count() if casos_beneficiario else 0
    total_donaciones = donaciones_realizadas.count() if donaciones_realizadas else 0
    
    context = {
        'usuario': usuario,
        'casos_beneficiario': casos_beneficiario,
        'donaciones_realizadas': donaciones_realizadas,
        'total_casos': total_casos,
        'total_donaciones': total_donaciones,
    }
    
    return render(request, 'members/perfil_usuario.html', context)


def lista_donaciones(request):
    """Lista todas las donaciones"""
    if not Donaciones:
        return render(request, 'members/lista_donaciones.html', {'donaciones': []})
    
    donaciones = (Donaciones.objects
                  .select_related('id_caso', 'id_donador')
                  .order_by('-fecha_compromiso')[:100])
    
    return render(request, 'members/lista_donaciones.html', {'donaciones': donaciones})


def lista_categorias(request):
    """Lista todas las categorías"""
    if not Categorias:
        return render(request, 'members/lista_categorias.html', {'categorias': []})
    
    categorias = Categorias.objects.all().order_by('nombre')
    
    return render(request, 'members/lista_categorias.html', {'categorias': categorias})


def lista_casos(request):
    """Lista casos con filtros opcionales"""
    if not Casos:
        return render(request, 'members/lista_casos.html', {'casos': []})
    
    casos = Casos.objects.select_related('id_beneficiario', 'id_estado').order_by('-fecha_creacion')
    
    # Filtro por categoría si viene en query params
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        try:
            casos = casos.filter(casocategorias__id_categoria_id=categoria_id)
        except Exception:
            pass
    
    return render(request, 'members/lista_casos.html', {'casos': casos})


@login_required_session
@require_http_methods(["GET", "POST"])
def editar_usuario(request, user_id):
    """Editar información de un usuario"""
    if not Usuarios:
        messages.error(request, "Modelo de usuarios no disponible.")
        return redirect('members:lista_usuarios')
    
    usuario = get_object_or_404(Usuarios, pk=user_id)
    
    if request.method == 'POST':
        usuario.nombres = request.POST.get('nombres', '').strip()
        usuario.apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        usuario.apellido_materno = request.POST.get('apellido_materno', '').strip()
        usuario.correo = request.POST.get('correo', '').strip()
        usuario.telefono = request.POST.get('telefono', '').strip()
        usuario.ciudad = request.POST.get('ciudad', '').strip()
        usuario.estado = request.POST.get('estado', '').strip()
        usuario.pais = request.POST.get('pais', '').strip()
        usuario.imagen_perfil = request.POST.get('imagen_perfil', '').strip() or None
        usuario.esta_activo = request.POST.get('esta_activo') == 'on'
        
        # Actualizar tipo de usuario
        tipo_id = request.POST.get('id_tipo_usuario')
        if tipo_id and TipoUsuario:
            try:
                tipo = TipoUsuario.objects.get(pk=tipo_id)
                usuario.id_tipo_usuario = tipo
            except TipoUsuario.DoesNotExist:
                pass
        
        try:
            usuario.save()
            messages.success(request, f"Usuario {usuario.nombres} actualizado exitosamente.")
            return redirect('members:perfil_usuario', user_id=usuario.id)
        except Exception as e:
            messages.error(request, f"Error al actualizar usuario: {str(e)}")
    
    tipos_usuario = TipoUsuario.objects.all() if TipoUsuario else []
    
    return render(request, 'members/editar_usuario.html', {
        'usuario': usuario,
        'tipos_usuario': tipos_usuario
    })


@login_required_session
@require_http_methods(["POST"])
def eliminar_usuario(request, user_id):
    """Eliminar un usuario"""
    if not Usuarios:
        messages.error(request, "Modelo de usuarios no disponible.")
        return redirect('members:lista_usuarios')
    
    # Evitar que se elimine a sí mismo
    if request.session.get('user_id') == user_id:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect('members:lista_usuarios')
    
    try:
        usuario = get_object_or_404(Usuarios, pk=user_id)
        nombre = f"{usuario.nombres} {usuario.apellido_paterno}"
        usuario.delete()
        messages.success(request, f"Usuario {nombre} eliminado exitosamente.")
    except Exception as e:
        messages.error(request, f"Error al eliminar usuario: {str(e)}")
    
    return redirect('members:lista_usuarios')


@login_required_session
@require_http_methods(["GET", "POST"])
def crear_caso(request):
    """
    Vista para crear un caso con validación completa y soporte para múltiples imágenes.
    """
    if request.method == "POST":
        if Casos and Usuarios and EstadoCaso:
            titulo = request.POST.get('titulo', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            entidad = request.POST.get('entidad', '').strip()
            direccion = request.POST.get('direccion', '').strip()
            colonia = request.POST.get('colonia', '').strip()
            codigo_postal = request.POST.get('codigo_postal', '').strip()
            
            # URLs de imágenes
            imagen1 = request.POST.get('imagen1', '').strip()
            imagen2 = request.POST.get('imagen2', '').strip()
            imagen3 = request.POST.get('imagen3', '').strip()
            imagen4 = request.POST.get('imagen4', '').strip()
            
            user_id = request.session.get('user_id')
            
            if not titulo:
                messages.error(request, "El título es obligatorio.")
                return render(request, 'members/crear_caso.html')
            
            try:
                beneficiario = Usuarios.objects.get(pk=user_id)
                
                # Obtener estado por defecto (Abierto)
                estado_default = EstadoCaso.objects.filter(nombre__iexact='Abierto').first()
                if not estado_default:
                    estado_default = EstadoCaso.objects.first()
                
                caso = Casos.objects.create(
                    id_beneficiario=beneficiario,
                    id_estado=estado_default,
                    titulo=titulo,
                    descripcion=descripcion,
                    entidad=entidad,
                    direccion=direccion,
                    colonia=colonia,
                    codigo_postal=codigo_postal,
                    imagen1=imagen1 or None,
                    imagen2=imagen2 or None,
                    imagen3=imagen3 or None,
                    imagen4=imagen4 or None,
                    esta_abierto=True,
                )
                
                messages.success(request, f"Caso '{titulo}' creado exitosamente.")
                return redirect('members:detalle_caso', caso_id=caso.id)
                
            except Usuarios.DoesNotExist:
                messages.error(request, "Usuario no encontrado. Por favor inicia sesión nuevamente.")
                return redirect('members:login')
            except Exception as e:
                messages.error(request, f"Error al crear el caso: {str(e)}")
        else:
            messages.error(request, "Modelo de casos no disponible.")
        
        return redirect('members:lista_casos')
    
    # GET request
    return render(request, 'members/crear_caso.html')


@login_required_session
@require_http_methods(["GET", "POST"])
def editar_caso(request, caso_id):
    """Editar caso existente"""
    if not Casos:
        messages.error(request, "Modelo de casos no disponible.")
        return redirect('members:lista_casos')
    
    caso = get_object_or_404(Casos, pk=caso_id)
    
    # Verificar que el usuario sea el beneficiario
    user_id = request.session.get('user_id')
    if caso.id_beneficiario_id != user_id:
        messages.error(request, "No tienes permiso para editar este caso.")
        return redirect('members:detalle_caso', caso_id=caso_id)
    
    if request.method == 'POST':
        caso.titulo = request.POST.get('titulo', '').strip()
        caso.descripcion = request.POST.get('descripcion', '').strip()
        caso.entidad = request.POST.get('entidad', '').strip()
        caso.direccion = request.POST.get('direccion', '').strip()
        caso.colonia = request.POST.get('colonia', '').strip()
        caso.codigo_postal = request.POST.get('codigo_postal', '').strip()
        
        caso.imagen1 = request.POST.get('imagen1', '').strip() or None
        caso.imagen2 = request.POST.get('imagen2', '').strip() or None
        caso.imagen3 = request.POST.get('imagen3', '').strip() or None
        caso.imagen4 = request.POST.get('imagen4', '').strip() or None
        
        try:
            caso.save()
            messages.success(request, "Caso actualizado exitosamente.")
            return redirect('members:detalle_caso', caso_id=caso.id)
        except Exception as e:
            messages.error(request, f"Error al actualizar: {str(e)}")
    
    return render(request, 'members/editar_caso.html', {'caso': caso})


@login_required_session
@require_http_methods(["GET", "POST"])
def crear_donacion(request, caso_id):
    """Crear donación para un caso"""
    if not (Donaciones and Casos and Usuarios):
        messages.error(request, "Modelos no disponibles.")
        return redirect('members:lista_casos')
    
    caso = get_object_or_404(Casos, pk=caso_id)
    user_id = request.session.get('user_id')
    
    if request.method == 'POST':
        monto_str = request.POST.get('monto', '0').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        try:
            monto = float(monto_str)
            if monto <= 0:
                messages.error(request, "El monto debe ser mayor a cero.")
                return render(request, 'members/crear_donacion.html', {'caso': caso})
            
            donador = Usuarios.objects.get(pk=user_id)
            
            donacion = Donaciones.objects.create(
                id_caso=caso,
                id_donador=donador,
                monto=monto,
                descripcion_donacion=descripcion,
                estado_donacion='Pendiente',
            )
            
            messages.success(request, f"¡Donación de ${monto} registrada exitosamente!")
            return redirect('members:detalle_caso', caso_id=caso.id)
            
        except ValueError:
            messages.error(request, "Monto inválido.")
        except Usuarios.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect('members:login')
        except Exception as e:
            messages.error(request, f"Error al crear donación: {str(e)}")
    
    return render(request, 'members/crear_donacion.html', {'caso': caso})


@login_required_session
@require_http_methods(["GET", "POST"])
def editar_usuario(request, user_id):
    """Editar información de un usuario"""
    if not Usuarios:
        messages.error(request, "Modelo de usuarios no disponible.")
        return redirect('members:lista_usuarios')
    
    usuario = get_object_or_404(Usuarios, pk=user_id)
    
    if request.method == 'POST':
        usuario.nombres = request.POST.get('nombres', '').strip()
        usuario.apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        usuario.apellido_materno = request.POST.get('apellido_materno', '').strip()
        usuario.correo = request.POST.get('correo', '').strip()
        usuario.telefono = request.POST.get('telefono', '').strip()
        usuario.ciudad = request.POST.get('ciudad', '').strip()
        usuario.estado = request.POST.get('estado', '').strip()
        usuario.pais = request.POST.get('pais', '').strip()
        usuario.imagen_perfil = request.POST.get('imagen_perfil', '').strip() or None
        usuario.esta_activo = request.POST.get('esta_activo') == 'on'
        
        # Actualizar tipo de usuario
        tipo_id = request.POST.get('id_tipo_usuario')
        if tipo_id and TipoUsuario:
            try:
                tipo = TipoUsuario.objects.get(pk=tipo_id)
                usuario.id_tipo_usuario = tipo
            except TipoUsuario.DoesNotExist:
                pass
        
        try:
            usuario.save()
            messages.success(request, f"Usuario {usuario.nombres} actualizado exitosamente.")
            return redirect('members:perfil_usuario', user_id=usuario.id)
        except Exception as e:
            messages.error(request, f"Error al actualizar usuario: {str(e)}")
    
    tipos_usuario = TipoUsuario.objects.all() if TipoUsuario else []
    
    return render(request, 'members/editar_usuario.html', {
        'usuario': usuario,
        'tipos_usuario': tipos_usuario
    })


@login_required_session
@require_http_methods(["POST"])
def eliminar_usuario(request, user_id):
    """Eliminar un usuario"""
    if not Usuarios:
        messages.error(request, "Modelo de usuarios no disponible.")
        return redirect('members:lista_usuarios')
    
    # Evitar que se elimine a sí mismo
    if request.session.get('user_id') == user_id:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect('members:lista_usuarios')
    
    try:
        usuario = get_object_or_404(Usuarios, pk=user_id)
        nombre = f"{usuario.nombres} {usuario.apellido_paterno}"
        usuario.delete()
        messages.success(request, f"Usuario {nombre} eliminado exitosamente.")
    except Exception as e:
        messages.error(request, f"Error al eliminar usuario: {str(e)}")
    
    return redirect('members:lista_usuarios')


@login_required_session
@require_http_methods(["GET"])
def obtener_datos_usuario(request, user_id):
    """API endpoint para obtener datos de un usuario en formato JSON"""
    if not Usuarios:
        return HttpResponse('{"error": "Modelo no disponible"}', content_type='application/json', status=400)
    
    try:
        usuario = Usuarios.objects.get(pk=user_id)
        
        data = {
            'nombres': usuario.nombres,
            'apellido_paterno': usuario.apellido_paterno,
            'apellido_materno': usuario.apellido_materno or '',
            'correo': usuario.correo,
            'telefono': usuario.telefono or '',
            'direccion': usuario.direccion or '',
            'colonia': usuario.colonia or '',
            'codigo_postal': usuario.codigo_postal or '',
            'ciudad': usuario.ciudad or '',
            'estado': usuario.estado or '',
            'imagen_perfil': usuario.imagen_perfil or '',
            'imagen_ine_frontal_url': usuario.imagen_ine_frontal_url or '',
            'imagen_ine_trasera_url': usuario.imagen_ine_trasera_url or '',
            'esta_activo': usuario.esta_activo,
            'verificado': usuario.verificado if hasattr(usuario, 'verificado') else False,
            'id_tipo_usuario': usuario.id_tipo_usuario.id if usuario.id_tipo_usuario else '',
        }
        
        import json
        return HttpResponse(json.dumps(data), content_type='application/json')
        
    except Usuarios.DoesNotExist:
        return HttpResponse('{"error": "Usuario no encontrado"}', content_type='application/json', status=404)
    except Exception as e:
        return HttpResponse(f'{{"error": "{str(e)}"}}', content_type='application/json', status=500)


@login_required_session
@role_required('Administrador')
def crear_usuario_modal(request):
    """Crear o editar usuario desde el modal"""
    if not Usuarios or not TipoUsuario:
        messages.error(request, "Modelos no disponibles.")
        return redirect('members:lista_usuarios')
    
    usuario_id = request.POST.get('usuario_id', '').strip()
    
    try:
        # Si hay usuario_id, es edición
        if usuario_id:
            usuario = get_object_or_404(Usuarios, pk=usuario_id)
            
            # Actualizar campos
            usuario.nombres = request.POST.get('nombres', '').strip()
            usuario.apellido_paterno = request.POST.get('apellido_paterno', '').strip()
            usuario.apellido_materno = request.POST.get('apellido_materno', '').strip()
            usuario.correo = request.POST.get('correo', '').strip()
            usuario.telefono = request.POST.get('telefono', '').strip()
            usuario.direccion = request.POST.get('direccion', '').strip()
            usuario.colonia = request.POST.get('colonia', '').strip()
            usuario.codigo_postal = request.POST.get('codigo_postal', '').strip()
            usuario.ciudad = request.POST.get('ciudad', '').strip()
            usuario.estado = request.POST.get('estado', '').strip()
            usuario.imagen_perfil = request.POST.get('imagen_perfil', '').strip() or None
            usuario.imagen_ine_frontal_url = request.POST.get('imagen_ine_frontal_url', '').strip() or None
            usuario.imagen_ine_trasera_url = request.POST.get('imagen_ine_trasera_url', '').strip() or None
            usuario.esta_activo = request.POST.get('esta_activo') == 'on'
            usuario.verificado = request.POST.get('verificado') == 'on'
            
            # Actualizar contraseña solo si se proporcionó una nueva
            nueva_contrasena = request.POST.get('contrasena', '').strip()
            if nueva_contrasena:
                usuario.contrasena = make_password(nueva_contrasena)
            
            # Actualizar tipo de usuario
            tipo_id = request.POST.get('id_tipo_usuario')
            if tipo_id:
                tipo = TipoUsuario.objects.get(pk=tipo_id)
                usuario.id_tipo_usuario = tipo
            
            usuario.save()
            messages.success(request, f"Usuario {usuario.nombres} actualizado exitosamente.")
            
        else:
            # Crear nuevo usuario
            nombres = request.POST.get('nombres', '').strip()
            apellido_paterno = request.POST.get('apellido_paterno', '').strip()
            correo = request.POST.get('correo', '').strip()
            contrasena = request.POST.get('contrasena', '').strip()
            tipo_id = request.POST.get('id_tipo_usuario')
            
            if not all([nombres, apellido_paterno, correo, contrasena, tipo_id]):
                messages.error(request, "Todos los campos obligatorios son requeridos.")
                return redirect('members:lista_usuarios')
            
            tipo = TipoUsuario.objects.get(pk=tipo_id)
            
            usuario = Usuarios.objects.create(
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=request.POST.get('apellido_materno', '').strip(),
                correo=correo,
                contrasena=make_password(contrasena),
                telefono=request.POST.get('telefono', '').strip(),
                direccion=request.POST.get('direccion', '').strip(),
                colonia=request.POST.get('colonia', '').strip(),
                codigo_postal=request.POST.get('codigo_postal', '').strip(),
                ciudad=request.POST.get('ciudad', '').strip(),
                estado=request.POST.get('estado', '').strip(),
                imagen_perfil=request.POST.get('imagen_perfil', '').strip() or None,
                imagen_ine_frontal_url=request.POST.get('imagen_ine_frontal_url', '').strip() or None,
                imagen_ine_trasera_url=request.POST.get('imagen_ine_trasera_url', '').strip() or None,
                esta_activo=request.POST.get('esta_activo') == 'on',
                verificado=request.POST.get('verificado') == 'on',
                id_tipo_usuario=tipo,
            )
            
            messages.success(request, f"Usuario {usuario.nombres} creado exitosamente.")
    
    except TipoUsuario.DoesNotExist:
        messages.error(request, "Tipo de usuario no válido.")
    except Exception as e:
        messages.error(request, f"Error al procesar usuario: {str(e)}")
    
    return redirect('members:lista_usuarios')