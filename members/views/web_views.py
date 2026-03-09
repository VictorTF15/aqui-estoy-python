from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# ============================================
# VISTAS DE AUTENTICACIÓN WEB
# ============================================

def login_view(request):
    """Vista de login para usuarios web"""
    return render(request, 'web/login.html')

def register_view(request):
    """Vista de registro para usuarios web"""
    return render(request, 'web/register.html')

# ============================================
# VISTAS PRINCIPALES WEB
# ============================================

def home_web(request):
    """Vista principal del dashboard web"""
    return render(request, 'web/home.html')

def perfil_web(request):
    """Vista del perfil de usuario web"""
    return render(request, 'web/perfil.html')

# ============================================
# VISTAS DE CASOS WEB
# ============================================

def lista_casos_web(request):
    """Vista de listado de casos web"""
    return render(request, 'web/casos/lista.html')

def detalle_caso_web(request, id):
    """Vista de detalle de un caso web"""
    context = {
        'caso_id': id
    }
    return render(request, 'web/casos/detalle.html', context)

def crear_caso_web(request):
    """Vista para crear un nuevo caso web"""
    return render(request, 'web/casos/crear.html')

# ============================================
# VISTAS DE DONACIONES WEB
# ============================================

def lista_donaciones_web(request):
    """Vista de listado de donaciones web"""
    return render(request, 'web/donaciones/lista.html')

def crear_donacion_web(request, caso_id):
    """Vista para crear una nueva donación web"""
    context = {
        'caso_id': caso_id
    }
    return render(request, 'web/donaciones/crear.html', context)