from django.apps import apps
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods  # AGREGAR ESTA LÍNEA
from .models import Casos, Categorias, EstadoCaso, Donaciones, CasoCategorias

from .decorators import login_required_session, role_required, anonymous_required

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
Estadoscasos = _get_model('Estadoscasos')
Tiposusuario = _get_model('Tiposusuario')

@login_required_session
def feed(request):
    user_id = request.session.get('user_id')
    role = request.session.get('user_role', '')
    
    context = {
        'role': role,
        'recientes': [],
        'categorias': [],
        'usuario': None,
        'stats': {},
    }
    
    if Usuarios and user_id:
        try:
            usuario = Usuarios.objects.get(pk=user_id)
            context['usuario'] = usuario
        except Usuarios.DoesNotExist:
            pass
    
    if Categorias:
        context['categorias'] = Categorias.objects.all()[:10]
    
    if role == 'Beneficiario':
        if Casos and user_id:
            mis_casos = Casos.objects.filter(id_beneficiario=user_id).select_related('id_estado').order_by('-fecha_creacion')
            context['mis_casos'] = mis_casos[:5]
            
            total_recaudado = 0
            if Donaciones:
                total_recaudado = Donaciones.objects.filter(
                    id_caso__id_beneficiario=user_id
                ).aggregate(total=Sum('monto'))['total'] or 0
            
            context['stats'] = {
                'mis_casos_total': mis_casos.count(),
                'mis_casos_activos': mis_casos.filter(id_estado__nombre='Activo').count(),
                'total_recaudado': total_recaudado,
            }
            
            context['recientes'] = mis_casos[:5]
    
    elif role == 'Donador':
        if Donaciones and user_id:
            mis_donaciones = Donaciones.objects.filter(
                id_donador=user_id
            ).select_related('id_caso').order_by('-fecha_compromiso')
            context['mis_donaciones'] = mis_donaciones[:5]
            
            total_donado = mis_donaciones.aggregate(total=Sum('monto'))['total'] or 0
            casos_apoyados = mis_donaciones.values('id_caso').distinct().count()
            
            context['stats'] = {
                'total_donado': total_donado,
                'casos_apoyados': casos_apoyados,
                'donaciones_realizadas': mis_donaciones.count(),
            }
        
        if Casos:
            context['recientes'] = Casos.objects.filter(
                id_estado__nombre='Activo'
            ).exclude(
                id_beneficiario=user_id
            ).select_related('id_estado', 'id_beneficiario').order_by('-fecha_creacion')[:5]
    
    elif role == 'Administrador':
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
        
        if Casos:
            context['recientes'] = Casos.objects.select_related('id_estado', 'id_beneficiario').order_by('-fecha_creacion')[:5]
    
    else:
        if Casos:
            context['recientes'] = Casos.objects.select_related('id_estado').order_by('-fecha_creacion')[:5]
    
    return render(request, 'members/feed.html', context)


@anonymous_required
def login_view(request):
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
                        if not usuario.esta_activo:
                            messages.error(request, "Tu cuenta está desactivada. Contacta al administrador.")
                            return render(request, 'members/login.html')
                        
                        request.session['user_id'] = usuario.id
                        request.session['user_name'] = f"{getattr(usuario,'nombres','')} {getattr(usuario,'apellido_paterno','')}".strip()
                        
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
                Usuarios.objects.create(correo=correo, nombres=nombres, contrasena=contrasena)
                messages.success(request, "Usuario creado correctamente.")
                return redirect('members:login')
            except Exception:
                messages.error(request, "Error al crear usuario en la base de datos.")
        else:
            messages.info(request, "Registro simulado (modelo Usuarios no encontrado).")
            return redirect('members:login')

    return render(request, 'members/register.html')


def logout_view(request):
    user_name = request.session.get('user_name', 'Usuario')
    request.session.flush()
    messages.success(request, f"Hasta pronto, {user_name}. Has cerrado sesión exitosamente.")
    return redirect('members:login')


@login_required_session
@role_required('Administrador')
def lista_usuarios(request):
    if not Usuarios:
        return render(request, 'members/lista_usuarios.html', {
            'usuarios': [],
            'tipos_usuario': []
        })
    
    # Cargar modelo TiposUsuario correctamente
    try:
        TiposUsuario = apps.get_model('members', 'Tiposusuario')
    except LookupError:
        TiposUsuario = None
    
    usuarios = Usuarios.objects.select_related('id_tipo_usuario').all()
    tipos_usuario = TiposUsuario.objects.all() if TiposUsuario else []
    
    context = {
        'usuarios': usuarios,
        'tipos_usuario': tipos_usuario,
    }
    
    return render(request, 'members/lista_usuarios.html', context)


@login_required_session
@role_required('Administrador')
def crear_usuario_modal(request):
    pass


@login_required_session
@role_required('Administrador')
def eliminar_usuario(request, user_id):
    pass


@login_required_session
@role_required('Beneficiario', 'Administrador')
def crear_caso(request):
    pass


# ============= VISTAS DE CASOS =============

@login_required_session
def lista_casos(request):
    """Vista para listar todos los casos"""
    if not Casos:
        return render(request, 'members/casos/lista_casos.html', {'casos': [], 'categorias': [], 'estados': []})
    
    casos = Casos.objects.select_related(
        'id_beneficiario', 
        'id_estado'
    ).filter(esta_abierto=True).order_by('-fecha_publicacion')
    
    # Filtros
    buscar = request.GET.get('buscar', '')
    categoria_id = request.GET.get('categoria', '')
    estado_id = request.GET.get('estado', '')
    colonia = request.GET.get('colonia', '')
    
    if buscar:
        casos = casos.filter(
            Q(titulo__icontains=buscar) |
            Q(descripcion__icontains=buscar) |
            Q(colonia__icontains=buscar)
        )
    
    if categoria_id:
        casos = casos.filter(casocategorias__id_categoria_id=categoria_id).distinct()
    
    if estado_id:
        casos = casos.filter(id_estado_id=estado_id)
    
    if colonia:
        casos = casos.filter(colonia__icontains=colonia)
    
    # Paginación
    paginator = Paginator(casos, 12)
    page = request.GET.get('page', 1)
    casos_paginados = paginator.get_page(page)
    
    # Obtener categorías y estados para los filtros
    categorias = Categorias.objects.filter(es_activo=True) if Categorias else []
    
    # Buscar el modelo de estados
    estados = []
    if Estadoscasos:
        estados = Estadoscasos.objects.all()
    elif EstadoCaso:
        estados = EstadoCaso.objects.all()
    
    context = {
        'casos': casos_paginados,
        'categorias': categorias,
        'estados': estados,
        'buscar': buscar,
        'categoria_seleccionada': categoria_id,
        'estado_seleccionado': estado_id,
        'colonia': colonia,
    }
    return render(request, 'members/casos/lista_casos.html', context)


@login_required_session
def detalle_caso(request, caso_id):
    """Vista para ver el detalle de un caso específico"""
    caso = get_object_or_404(Casos, id=caso_id)
    
    context = {
        'caso': caso,
    }
    return render(request, 'members/casos/detalle_caso.html', context)


@login_required_session
def editar_caso(request, caso_id):
    """Vista para editar un caso existente"""
    caso = get_object_or_404(Casos, id=caso_id)
    
    if request.method == 'POST':
        caso.titulo = request.POST.get('titulo')
        caso.descripcion = request.POST.get('descripcion')
        caso.save()
        messages.success(request, 'Caso actualizado exitosamente')
        return redirect('members:detalle_caso', caso_id=caso.id)
    
    context = {
        'caso': caso,
    }
    return render(request, 'members/casos/editar_caso.html', context)


@login_required_session
@role_required('Beneficiario', 'Administrador')
def crear_caso(request):
    """Vista para crear un nuevo caso"""
    if request.method == 'POST':
        # Lógica para crear caso
        pass
    
    return render(request, 'members/casos/crear_caso.html')


@login_required_session
def mis_casos(request):
    """Vista para que el beneficiario vea sus propios casos"""
    user_id = request.session.get('user_id')
    
    if not Casos or not user_id:
        return render(request, 'members/casos/mis_casos.html', {'casos': []})
    
    casos = Casos.objects.filter(id_beneficiario_id=user_id).order_by('-fecha_creacion')
    
    context = {
        'casos': casos,
    }
    return render(request, 'members/casos/mis_casos.html', context)


@login_required_session
def compartir_caso(request, caso_id):
    """Incrementar contador de veces compartido"""
    caso = get_object_or_404(Casos, id=caso_id)
    caso.compartido += 1
    caso.save(update_fields=['compartido'])
    
    return JsonResponse({
        'success': True,
        'compartido': caso.compartido
    })


@login_required_session
@role_required('Administrador')
def crear_usuario_modal(request):
    """Crear o editar usuario desde el modal"""
    if not Usuarios or not TipoUsuario:
        messages.error(request, "Modelos no disponibles.")
        return redirect('members:lista_usuarios')
    
    usuario_id = request.POST.get('usuario_id', '').strip()
    
    try:
        if usuario_id:
            usuario = get_object_or_404(Usuarios, pk=usuario_id)
            
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
            
            nueva_contrasena = request.POST.get('contrasena', '').strip()
            if nueva_contrasena:
                usuario.contrasena = make_password(nueva_contrasena)
            
            tipo_id = request.POST.get('id_tipo_usuario')
            if tipo_id:
                tipo = TipoUsuario.objects.get(pk=tipo_id)
                usuario.id_tipo_usuario = tipo
            
            usuario.save()
            messages.success(request, f"Usuario {usuario.nombres} actualizado exitosamente.")
            
        else:
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


@login_required_session
def mapa_casos(request):
    """Mapa interactivo de casos"""
    context = {
        'role': request.session.get('user_role', ''),
    }
    
    if Categorias:
        context['categorias'] = Categorias.objects.all()
    
    if EstadoCaso:
        context['estados'] = EstadoCaso.objects.all()
    
    return render(request, 'members/mapa_casos.html', context)


def api_casos_mapa(request):
    """API para obtener casos para el mapa"""
    try:
        from decimal import Decimal
        
        # Obtener filtros
        categoria_id = request.GET.get('categoria')
        estado_id = request.GET.get('estado')
        
        print(f"\n{'='*60}")
        print(f"API CASOS MAPA - REQUEST")
        print(f"{'='*60}")
        print(f"Filtro categoría: {categoria_id}")
        print(f"Filtro estado: {estado_id}")
        
        # Query base con coordenadas válidas
        casos = Casos.objects.select_related(
            'id_estado',
            'id_beneficiario'
        ).filter(
            latitud__isnull=False,
            longitud__isnull=False,
            esta_abierto=True
        ).exclude(
            latitud=0,
            longitud=0
        )
        
        print(f"\n📊 Total casos con coordenadas: {casos.count()}")
        
        # Aplicar filtros
        if categoria_id:
            casos = casos.filter(casocategorias__id_categoria_id=categoria_id).distinct()
            print(f"   Filtrado por categoría {categoria_id}: {casos.count()} casos")
        
        if estado_id:
            casos = casos.filter(id_estado_id=estado_id)
            print(f"   Filtrado por estado {estado_id}: {casos.count()} casos")
        
        # Construir respuesta
        casos_data = []
        
        for idx, caso in enumerate(casos):
            print(f"\n📍 Procesando caso {idx + 1}/{casos.count()}")
            print(f"   ID: {caso.id}")
            print(f"   Título: {caso.titulo}")
            print(f"   Latitud raw: {caso.latitud} (tipo: {type(caso.latitud)})")
            print(f"   Longitud raw: {caso.longitud} (tipo: {type(caso.longitud)})")
            
            # Validar y convertir coordenadas
            try:
                if isinstance(caso.latitud, Decimal):
                    lat = float(caso.latitud)
                else:
                    lat = float(caso.latitud) if caso.latitud else 0
                    
                if isinstance(caso.longitud, Decimal):
                    lng = float(caso.longitud)
                else:
                    lng = float(caso.longitud) if caso.longitud else 0
                
                print(f"   ✓ Coordenadas convertidas: lat={lat}, lng={lng}")
                
                # Verificar que las coordenadas estén en rango válido
                if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                    print(f"   ⚠️  ADVERTENCIA: Coordenadas fuera de rango")
                    continue
                
                if lat == 0 and lng == 0:
                    print(f"   ⚠️  ADVERTENCIA: Coordenadas en (0,0)")
                    continue
                    
            except (ValueError, TypeError) as e:
                print(f"   ❌ ERROR: No se pudieron convertir las coordenadas: {e}")
                continue
            
            # Obtener imagen principal
            imagen_url = None
            for img_field in ['imagen1', 'imagen2', 'imagen3', 'imagen4']:
                if hasattr(caso, img_field):
                    img_value = getattr(caso, img_field)
                    if img_value:
                        imagen_url = img_value
                        break
            
            # Obtener categorías del caso
            categorias_caso = []
            try:
                caso_categorias = CasoCategorias.objects.filter(
                    id_caso=caso
                ).select_related('id_categoria')
                
                categorias_caso = [cc.id_categoria.nombre for cc in caso_categorias]
            except Exception as e:
                print(f"   ⚠️  Error obteniendo categorías: {e}")
            
            categoria_principal = categorias_caso[0] if categorias_caso else 'Sin categoría'
            
            # Obtener nombre del beneficiario
            beneficiario_nombre = 'Sin beneficiario'
            if caso.id_beneficiario:
                try:
                    beneficiario_nombre = f"{caso.id_beneficiario.nombres} {caso.id_beneficiario.apellido_paterno}".strip()
                except Exception as e:
                    print(f"   ⚠️  Error obteniendo beneficiario: {e}")
            
            # Preparar descripción
            descripcion = caso.descripcion if caso.descripcion else ''
            if len(descripcion) > 150:
                descripcion = descripcion[:150] + '...'
            
            estado_nombre = caso.id_estado.nombre if caso.id_estado else 'Sin estado'
            
            caso_dict = {
                'id': caso.id,
                'titulo': caso.titulo,
                'descripcion': descripcion,
                'lat': lat,  # ← CAMPO CRÍTICO
                'lng': lng,  # ← CAMPO CRÍTICO
                'estado': estado_nombre,
                'categoria': categoria_principal,
                'categorias': categorias_caso,
                'colonia': caso.colonia or 'No especificada',
                'beneficiario': beneficiario_nombre,
                'imagen': imagen_url,
                'url': f"/casos/{caso.id}/",
            }
            
            print(f"   ✅ Caso agregado: lat={caso_dict['lat']}, lng={caso_dict['lng']}")
            casos_data.append(caso_dict)
        
        print(f"\n{'='*60}")
        print(f"RESUMEN DE RESPUESTA")
        print(f"{'='*60}")
        print(f"Total casos en respuesta: {len(casos_data)}")
        
        # Imprimir primer caso para verificar estructura
        if casos_data:
            print(f"\nPrimer caso de ejemplo:")
            print(f"  Keys: {list(casos_data[0].keys())}")
            print(f"  lat: {casos_data[0].get('lat')}")
            print(f"  lng: {casos_data[0].get('lng')}")
        
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'success': True,
            'casos': casos_data,
            'total': len(casos_data)
        })
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n{'='*60}")
        print(f"❌ ERROR EN API_CASOS_MAPA")
        print(f"{'='*60}")
        print(error_detail)
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'success': False,
            'error': str(e),
            'casos': [],
            'total': 0
        }, status=500)


# ============= VISTAS DE USUARIOS =============

@login_required
def lista_usuarios(request):
    """Vista para listar todos los usuarios"""
    if not Usuarios:
        return render(request, 'members/lista_usuarios.html', {
            'usuarios': [],
            'tipos_usuario': []
        })
    
    # Cargar modelo TiposUsuario correctamente
    try:
        TiposUsuario = apps.get_model('members', 'Tiposusuario')
    except LookupError:
        TiposUsuario = None
    
    usuarios = Usuarios.objects.select_related('id_tipo_usuario').all()
    tipos_usuario = TiposUsuario.objects.all() if TiposUsuario else []
    
    context = {
        'usuarios': usuarios,
        'tipos_usuario': tipos_usuario,
    }
    
    return render(request, 'members/lista_usuarios.html', context)


@login_required
def perfil_usuario(request, user_id):
    """Vista para ver el perfil de un usuario"""
    if not Usuarios:
        return redirect('members:lista_usuarios')
    
    # Cargar modelos necesarios
    try:
        Donaciones = apps.get_model('members', 'Donaciones')
    except LookupError:
        Donaciones = None
    
    usuario = get_object_or_404(Usuarios.objects.select_related('id_tipo_usuario'), id=user_id)
    
    # Casos donde es beneficiario
    casos_beneficiario = []
    if Casos:
        casos_beneficiario = Casos.objects.filter(
            id_beneficiario=usuario
        ).select_related('id_estado').order_by('-fecha_creacion')
    
    # Donaciones realizadas
    donaciones_realizadas = []
    if Donaciones:
        donaciones_realizadas = Donaciones.objects.filter(
            id_donador=usuario
        ).select_related('id_caso').order_by('-fecha_compromiso')
    
    context = {
        'usuario': usuario,
        'casos_beneficiario': casos_beneficiario,
        'total_casos': casos_beneficiario.count() if casos_beneficiario else 0,
        'donaciones_realizadas': donaciones_realizadas,
        'total_donaciones': len(donaciones_realizadas),
    }
    
    return render(request, 'members/perfil_usuario.html', context)


@login_required
def obtener_datos_usuario(request, user_id):
    """API para obtener datos de un usuario (para edición)"""
    if not Usuarios:
        return JsonResponse({'error': 'Modelo no disponible'}, status=400)
    
    try:
        usuario = Usuarios.objects.get(id=user_id)
        
        data = {
            'nombres': usuario.nombres,
            'apellido_paterno': usuario.apellido_paterno,
            'apellido_materno': usuario.apellido_materno or '',
            'correo': usuario.correo,
            'telefono': usuario.telefono or '',
            'id_tipo_usuario': usuario.id_tipo_usuario.id if usuario.id_tipo_usuario else '',
            'direccion': usuario.direccion or '',
            'colonia': usuario.colonia or '',
            'codigo_postal': usuario.codigo_postal or '',
            'ciudad': usuario.ciudad or '',
            'estado': usuario.estado or '',
            'imagen_perfil': usuario.imagen_perfil or '',
            'imagen_ine_frontal_url': usuario.imagen_ine_frontal_url or '',
            'imagen_ine_trasera_url': usuario.imagen_ine_trasera_url or '',
            'esta_activo': usuario.esta_activo,
            'verificado': usuario.verificado,
        }
        
        return JsonResponse(data)
        
    except Usuarios.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def editar_usuario(request, user_id):
    """Vista para editar un usuario (alias de crear_usuario_modal)"""
    if request.method == 'POST':
        return crear_usuario_modal(request)
    
    # Si es GET, redirigir a lista de usuarios
    return redirect('members:lista_usuarios')

@login_required
@require_http_methods(["POST"])
def crear_usuario_modal(request):
    """Vista para crear o editar usuario desde modal"""
    if not Usuarios:
        messages.error(request, 'Modelo de usuarios no disponible')
        return redirect('members:lista_usuarios')
    
    try:
        # Cargar modelo TiposUsuario
        try:
            TiposUsuario = apps.get_model('members', 'Tiposusuario')
        except LookupError:
            TiposUsuario = None
        
        usuario_id = request.POST.get('usuario_id')
        
        # Datos del formulario
        data = {
            'nombres': request.POST.get('nombres'),
            'apellido_paterno': request.POST.get('apellido_paterno'),
            'apellido_materno': request.POST.get('apellido_materno', ''),
            'correo': request.POST.get('correo'),
            'telefono': request.POST.get('telefono', ''),
            'direccion': request.POST.get('direccion', ''),
            'colonia': request.POST.get('colonia', ''),
            'codigo_postal': request.POST.get('codigo_postal', ''),
            'ciudad': request.POST.get('ciudad', ''),
            'estado': request.POST.get('estado', ''),
            'imagen_perfil': request.POST.get('imagen_perfil', ''),
            'imagen_ine_frontal_url': request.POST.get('imagen_ine_frontal_url', ''),
            'imagen_ine_trasera_url': request.POST.get('imagen_ine_trasera_url', ''),
            'esta_activo': request.POST.get('esta_activo') == 'on',
            'verificado': request.POST.get('verificado') == 'on',
        }
        
        # Obtener tipo de usuario
        tipo_usuario_id = request.POST.get('id_tipo_usuario')
        if TiposUsuario and tipo_usuario_id:
            data['id_tipo_usuario'] = TiposUsuario.objects.get(id=tipo_usuario_id)
        
        # Crear o actualizar
        if usuario_id:
            # Actualizar usuario existente
            usuario = Usuarios.objects.get(id=usuario_id)
            for key, value in data.items():
                setattr(usuario, key, value)
            
            # Actualizar contraseña solo si se proporcionó una nueva
            nueva_contrasena = request.POST.get('contrasena')
            if nueva_contrasena:
                usuario.contrasena = make_password(nueva_contrasena)
            
            usuario.save()
            messages.success(request, f'Usuario {usuario.nombres} actualizado correctamente')
        else:
            # Crear nuevo usuario
            contrasena = request.POST.get('contrasena')
            if not contrasena:
                messages.error(request, 'La contraseña es obligatoria para nuevos usuarios')
                return redirect('members:lista_usuarios')
            
            data['contrasena'] = make_password(contrasena)
            usuario = Usuarios.objects.create(**data)
            messages.success(request, f'Usuario {usuario.nombres} creado correctamente')
        
        return redirect('members:lista_usuarios')
        
    except Exception as e:
        messages.error(request, f'Error al guardar usuario: {str(e)}')
        return redirect('members:lista_usuarios')

@login_required
@require_http_methods(["POST"])
def eliminar_usuario(request, user_id):
    """Vista para eliminar un usuario"""
    if not Usuarios:
        messages.error(request, 'Modelo de usuarios no disponible')
        return redirect('members:lista_usuarios')
    
    try:
        usuario = Usuarios.objects.get(id=user_id)
        nombre_completo = f"{usuario.nombres} {usuario.apellido_paterno}"
        usuario.delete()
        messages.success(request, f'Usuario {nombre_completo} eliminado correctamente')
    except Usuarios.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
    except Exception as e:
        messages.error(request, f'Error al eliminar usuario: {str(e)}')
    
    return redirect('members:lista_usuarios')


# ============= VISTAS DE CATEGORÍAS =============

def lista_categorias(request):
    """Vista para listar categorías"""
    categorias = Categorias.objects.filter(es_activo=True).annotate(
        total_casos=Count('casocategorias')
    )
    
    context = {
        'categorias': categorias,
    }
    return render(request, 'members/lista_categorias.html', context)


# ============= VISTAS DE DONACIONES =============

@login_required_session
def lista_donaciones(request):
    """Vista para listar todas las donaciones"""
    if not Donaciones:
        return render(request, 'members/lista_donaciones.html', {'donaciones': []})
    
    donaciones = Donaciones.objects.select_related(
        'id_donador',
        'id_caso'
    ).order_by('-fecha_compromiso')
    
    # Filtros
    estado = request.GET.get('estado', '')
    caso_id = request.GET.get('caso', '')
    
    if estado:
        donaciones = donaciones.filter(estado_donacion=estado)
    
    if caso_id:
        donaciones = donaciones.filter(id_caso_id=caso_id)
    
    # Paginación
    paginator = Paginator(donaciones, 20)
    page = request.GET.get('page', 1)
    donaciones_paginadas = paginator.get_page(page)
    
    context = {
        'donaciones': donaciones_paginadas,
        'estado_seleccionado': estado,
        'caso_seleccionado': caso_id,
        'role': request.session.get('user_role', ''),
    }
    return render(request, 'members/lista_donaciones.html', context)


@login_required_session
def crear_donacion(request, caso_id):
    """Vista para crear una nueva donación"""
    caso = get_object_or_404(Casos, id=caso_id)
    
    if request.method == 'POST':
        # Lógica para crear donación
        pass
    
    context = {
        'caso': caso,
    }
    return render(request, 'members/donaciones/crear_donacion.html', context)


@login_required_session
def mis_donaciones(request):
    """Vista para que el donador vea sus propias donaciones"""
    user_id = request.session.get('user_id')
    
    if not Donaciones or not user_id:
        return render(request, 'members/donaciones/mis_donaciones.html', {'donaciones': []})
    
    donaciones = Donaciones.objects.filter(
        id_donador_id=user_id
    ).select_related('id_caso').order_by('-fecha_compromiso')
    
    context = {
        'donaciones': donaciones,
    }
    return render(request, 'members/donaciones/mis_donaciones.html', context)


# ============= VISTAS DE ADMINISTRACIÓN =============

@login_required_session
@role_required('Administrador')
def admin(request):
    """Panel de administración"""
    stats = {}
    
    if Casos:
        stats['total_casos'] = Casos.objects.count()
        stats['casos_activos'] = Casos.objects.filter(id_estado__nombre='Activo').count()
        stats['casos_completados'] = Casos.objects.filter(id_estado__nombre='Completado').count()
        stats['casos_pendientes'] = Casos.objects.filter(id_estado__nombre='Pendiente').count()
    
    if Usuarios:
        stats['total_usuarios'] = Usuarios.objects.count()
        stats['usuarios_activos'] = Usuarios.objects.filter(esta_activo=True).count()
        stats['beneficiarios'] = Usuarios.objects.filter(id_tipo_usuario__nombre='Beneficiario').count()
        stats['donadores'] = Usuarios.objects.filter(id_tipo_usuario__nombre='Donador').count()
    
    if Donaciones:
        stats['total_donaciones'] = Donaciones.objects.count()
        stats['monto_total'] = Donaciones.objects.aggregate(Sum('monto'))['monto__sum'] or 0
        stats['donaciones_completadas'] = Donaciones.objects.filter(estado_donacion='Completado').count()
    
    if Categorias:
        stats['total_categorias'] = Categorias.objects.filter(es_activo=True).count()
    
    context = {
        'stats': stats,
        'role': request.session.get('user_role', ''),
    }
    
    return render(request, 'members/admin.html', context)