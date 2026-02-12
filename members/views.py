from django.apps import apps
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.template.loader import select_template
from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from django.db.models import Sum, Count

from .models import Usuarios, Casos, Donaciones, CasoCategorias, Categorias, EstadoCaso, TipoUsuario

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

# Login robusto
def login_view(request):
    """
    Login robusto: intenta renderizar plantillas existentes (preferencia: members/login.html),
    y si no hay ninguna disponible devuelve un formulario HTML minimal inline para que la URL funcione.
    """
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        contrasena = request.POST.get('contrasena', '')
        usuario = None
        if Usuarios:
            try:
                usuario = Usuarios.objects.filter(correo=correo).first()
            except Exception:
                usuario = None
        if usuario:
            raw_pass = getattr(usuario, 'contrasena', '') or getattr(usuario, 'password', '')
            ok = False
            try:
                ok = check_password(contrasena, raw_pass)
            except Exception:
                ok = (contrasena == raw_pass)
            if ok:
                request.session['user_id'] = usuario.id
                request.session['user_name'] = f"{getattr(usuario,'nombres','')} {getattr(usuario,'apellido_paterno','')}".strip()
                # extraer rol si existe
                role = ''
                for attr in ('id_tipo_usuario', 'idTipoUsuario', 'tipo_usuario', 'rol', 'role'):
                    val = getattr(usuario, attr, None)
                    if val:
                        role = getattr(val, 'nombre', str(val))
                        break
                request.session['user_role'] = role
                return redirect('members:feed')
        messages.error(request, "Credenciales inválidas.")

    # intentar templates existentes en el proyecto (no se crean ni sobrescriben)
    try:
        tpl = select_template(['members/login.html', 'login.html', 'members/register.html'])
        context = {}
        return HttpResponse(tpl.render(context, request))
    except TemplateDoesNotExist:
        # fallback mínimo inline (no archivo)
        html = """
        <!doctype html><html lang="es"><head><meta charset="utf-8"><title>Login</title></head>
        <body>
        <h2>Iniciar sesión</h2>
        {% if messages %}{% for m in messages %}<div style="color:red">{{ m }}</div>{% endfor %}{% endif %}
        <form method="post">{% csrf_token %}
          <label>Correo</label><br><input type="email" name="correo" required><br>
          <label>Contraseña</label><br><input type="password" name="contrasena" required><br><br>
          <button type="submit">Entrar</button>
          <a href="{% url 'members:register' %}">Registrar</a>
        </form>
        </body></html>
        """
        return HttpResponse(html)

# Lista de usuarios segura
def lista_usuarios(request):
    usuarios = Usuarios.objects.all() if Usuarios else []
    return render(request, 'members/lista_usuarios.html', {'usuarios': usuarios})

# Lista de donaciones segura
def lista_donaciones(request):
    donaciones = Donaciones.objects.select_related() .all().order_by('-id')[:200] if Donaciones else []
    return render(request, 'members/lista_donaciones.html', {'donaciones': donaciones})

# intentar resolver modelos de forma segura (si no existen, quedarán como None)
try:
    Casos = apps.get_model('members', 'Casos')
except Exception:
    Casos = None
try:
    Usuarios = apps.get_model('members', 'Usuarios')
except Exception:
    Usuarios = None
try:
    Donaciones = apps.get_model('members', 'Donaciones')
except Exception:
    Donaciones = None
try:
    CasoCategorias = apps.get_model('members', 'CasoCategorias')
except Exception:
    CasoCategorias = None

def feed(request):
    """
    Feed sin valores monetarios. Contextos por rol: Beneficiario, Donador, Otros.
    """
    user_id = request.session.get('user_id')
    usuario = Usuarios.objects.select_related('id_tipo_usuario').filter(pk=user_id).first() if Usuarios and user_id else None

    # extraer nombre de rol si existe relación
    role = ''
    if usuario:
        for attr in ('id_tipo_usuario', 'tipo_usuario', 'idTipoUsuario', 'rol', 'role'):
            val = getattr(usuario, attr, None)
            if val:
                role = getattr(val, 'nombre', str(val))
                break

    recientes = Casos.objects.select_related('id_estado','id_beneficiario').order_by('-fecha_creacion')[:8] if Casos else []
    categorias = Categorias.objects.all() if Categorias else []

    stats = {
        'total_casos': Casos.objects.count() if Casos else 0,
        'total_usuarios': Usuarios.objects.count() if Usuarios else 0,
        # ahora solo contamos registros de donaciones (sin sumar montos)
        'total_donaciones_count': Donaciones.objects.count() if Donaciones else 0,
    }

    context = {
        'usuario': usuario,
        'role': role,
        'recientes': recientes,
        'categorias': categorias,
        'stats': stats,
    }

    if role == 'Beneficiario' and Casos:
        context['mis_casos'] = Casos.objects.filter(id_beneficiario_id=user_id).select_related('id_estado').order_by('-fecha_creacion')
    elif role == 'Donador' and Donaciones and Casos:
        context['mis_donaciones'] = Donaciones.objects.filter(id_donador_id=user_id).select_related('id_caso').order_by('-id')[:50]
        # recomendados: casos abiertos (campo soft, lo intento detectar)
        try:
            recomendados_qs = Casos.objects.filter(esta_abierto=True).order_by('-fecha_creacion')[:8]
        except Exception:
            recomendados_qs = Casos.objects.order_by('-fecha_creacion')[:8]
        context['recomendados'] = recomendados_qs
    else:
        # top por número de donaciones por caso (si Donaciones existe)
        if Donaciones:
            top = (Donaciones.objects.values('id_caso')
                   .annotate(count=Count('id'))
                   .order_by('-count')[:10])
            caso_ids = [t['id_caso'] for t in top]
            casos_top = list(Casos.objects.filter(id__in=caso_ids).select_related('id_beneficiario')) if Casos else []
            context.update({'casos_top': casos_top, 'top_stats': top})

    return render(request, 'members/feed.html', context)

# Vistas mínimas requeridas por el menú (si ya existen, no sobrescribas)
def lista_casos(request):
    casos = Casos.objects.select_related('id_estado','id_beneficiario').order_by('-fecha_creacion') if Casos else []
    return render(request, 'members/lista_casos.html', {'casos': casos})

def detalle_caso(request, caso_id):
    if not Casos:
        return render(request, 'members/detalle_caso.html', {'caso': None})
    caso = get_object_or_404(Casos, pk=caso_id)
    return render(request, 'members/detalle_caso.html', {'caso': caso})

def lista_usuarios(request):
    usuarios = Usuarios.objects.all() if Usuarios else []
    return render(request, 'members/lista_usuarios.html', {'usuarios': usuarios})

def perfil_usuario(request, user_id):
    if not Usuarios:
        return render(request, 'members/perfil_usuario.html', {'usuario': None})
    usuario = get_object_or_404(Usuarios, pk=user_id)
    return render(request, 'members/perfil_usuario.html', {'usuario': usuario})

def lista_donaciones(request):
    donaciones = Donaciones.objects.select_related('id_caso','id_donador').order_by('-fecha')[:100] if Donaciones else []
    return render(request, 'members/lista_donaciones.html', {'donaciones': donaciones})

def lista_categorias(request):
    categorias = CasoCategorias.objects.all() if CasoCategorias else []
    return render(request, 'members/lista_categorias.html', {'categorias': categorias})

@require_http_methods(["GET", "POST"])
def crear_caso(request):
    """
    Vista mínima para crear un caso desde el formulario.
    Si el modelo Casos no existe no hará nada y solo redirige.
    """
    if request.method == "POST":
        if Casos:
            titulo = request.POST.get('titulo', 'Caso sin título')
            descripcion = request.POST.get('descripcion', '')
            user_id = request.session.get('user_id')
            payload = {'titulo': titulo, 'descripcion': descripcion}
            # si el modelo tiene campo id_beneficiario, intentar asignar el usuario logueado
            if Casos and Usuarios and any(f.name == 'id_beneficiario' for f in Casos._meta.fields):
                try:
                    beneficiario = Usuarios.objects.get(pk=user_id) if user_id else None
                    if beneficiario:
                        payload['id_beneficiario'] = beneficiario
                except Exception:
                    pass
            try:
                Casos.objects.create(**payload)
            except Exception:
                # crear silenciosamente si falla (puedes loggear si quieres)
                pass
        return redirect('members:lista_casos')
    return render(request, 'members/crear_caso.html')

@require_http_methods(["GET", "POST"])
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

# Añadir implementaciones mínimas solo si no existen
from django.apps import apps

if 'feed' not in globals():
    def feed(request):
        from django.shortcuts import render
        Usuarios = apps.get_model('members', 'Usuarios') if apps.is_installed('members') else None
        Casos = apps.get_model('members', 'Casos') if apps.is_installed('members') else None
        user_id = request.session.get('user_id')
        usuario = None
        if Usuarios and user_id:
            try:
                usuario = Usuarios.objects.get(pk=user_id)
            except Exception:
                usuario = None
        casos_recientes = Casos.objects.select_related('id_estado').order_by('-fecha_creacion')[:12] if Casos else []
        historial = Casos.objects.filter(id_beneficiario_id=user_id).order_by('-fecha_creacion')[:20] if Casos and user_id else (Casos.objects.order_by('-fecha_creacion')[:20] if Casos else [])
        return render(request, 'members/feed.html', {'usuario': usuario, 'casos_recientes': casos_recientes, 'historial': historial})

if 'crear_caso' not in globals():
    def crear_caso(request):
        from django.shortcuts import render, redirect
        Casos = apps.get_model('members', 'Casos') if apps.is_installed('members') else None
        Usuarios = apps.get_model('members', 'Usuarios') if apps.is_installed('members') else None
        if request.method == 'POST' and Casos:
            titulo = request.POST.get('titulo', 'Caso sin título')
            descripcion = request.POST.get('descripcion', '')
            payload = {'titulo': titulo, 'descripcion': descripcion}
            try:
                # si existe id_beneficiario como FK asignar usuario logueado
                if Usuarios and any(f.name == 'id_beneficiario' for f in Casos._meta.fields):
                    user_id = request.session.get('user_id')
                    if user_id:
                        payload['id_beneficiario_id'] = user_id
                Casos.objects.create(**payload)
            except Exception:
                pass
            return redirect('members:lista_casos')
        return render(request, 'members/crear_caso.html')

if 'login_view' not in globals():
    def login_view(request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from django.contrib.auth.hashers import check_password
        Usuarios = apps.get_model('members', 'Usuarios') if apps.is_installed('members') else None
        if request.method == 'POST' and Usuarios:
            correo = request.POST.get('correo', '').strip()
            contrasena = request.POST.get('contrasena', '')
            try:
                usuario = Usuarios.objects.get(correo=correo)
            except Exception:
                usuario = None
            if usuario:
                ok = False
                try:
                    ok = check_password(contrasena, getattr(usuario, 'contrasena', '') )
                except Exception:
                    ok = (contrasena == getattr(usuario, 'contrasena', ''))
                if ok:
                    request.session['user_id'] = usuario.id
                    request.session['user_name'] = f"{getattr(usuario,'nombres','')} {getattr(usuario,'apellido_paterno','')}".strip()
                    request.session['user_role'] = getattr(usuario, 'id_tipo_usuario', '') or ''
                    return redirect('members:feed')
            messages.error(request, "Credenciales inválidas.")
        return render(request, 'members/login.html')

if 'logout_view' not in globals():
    from django.shortcuts import redirect

    def logout_view(request):
        """
        Cierra la sesión limpiando la session y redirige al login.
        """
        try:
            request.session.flush()
        except Exception:
            # limpiar manualmente si flush falla
            for k in list(request.session.keys()):
                del request.session[k]
        return redirect('members:login')