from django.shortcuts import render, get_object_or_404
from .models import (
    Usuarios, Casos, Donaciones, Categorias, 
    Evidencias, TipoUsuario, EstadoCaso
)

def index(request):
    """Página principal con resumen general"""
    total_casos = Casos.objects.count()
    total_usuarios = Usuarios.objects.count()
    total_donaciones = Donaciones.objects.count()
    
    casos_recientes = Casos.objects.order_by('-fecha_creacion')[:5]
    
    context = {
        'total_casos': total_casos,
        'total_usuarios': total_usuarios,
        'total_donaciones': total_donaciones,
        'casos_recientes': casos_recientes,
    }
    return render(request, 'members/index.html', context)


def lista_casos(request):
    """Lista todos los casos"""
    casos = Casos.objects.select_related('id_beneficiario', 'id_estado').all()
    
    context = {
        'casos': casos,
    }
    return render(request, 'members/lista_casos.html', context)


def detalle_caso(request, caso_id):
    """Muestra el detalle de un caso específico"""
    caso = get_object_or_404(Casos, id=caso_id)
    evidencias = Evidencias.objects.filter(id_caso=caso)
    donaciones = Donaciones.objects.filter(id_caso=caso).select_related('id_donador')
    
    # Calcular porcentaje de progreso
    if caso.monto_objetivo > 0:
        porcentaje = (caso.monto_recaudado / caso.monto_objetivo) * 100
    else:
        porcentaje = 0
    
    context = {
        'caso': caso,
        'evidencias': evidencias,
        'donaciones': donaciones,
        'porcentaje': porcentaje,
    }
    return render(request, 'members/detalle_caso.html', context)


def lista_usuarios(request):
    """Lista todos los usuarios"""
    usuarios = Usuarios.objects.select_related('id_tipo_usuario').all()
    
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'members/lista_usuarios.html', context)


def detalle_usuario(request, usuario_id):
    """Muestra el detalle de un usuario"""
    usuario = get_object_or_404(Usuarios, id=usuario_id)
    casos_beneficiario = Casos.objects.filter(id_beneficiario=usuario)
    donaciones_realizadas = Donaciones.objects.filter(id_donador=usuario)
    
    context = {
        'usuario': usuario,
        'casos_beneficiario': casos_beneficiario,
        'donaciones_realizadas': donaciones_realizadas,
    }
    return render(request, 'members/detalle_usuario.html', context)


def lista_donaciones(request):
    """Lista todas las donaciones"""
    donaciones = Donaciones.objects.select_related('id_donador', 'id_caso').order_by('-fecha_compromiso')
    
    context = {
        'donaciones': donaciones,
    }
    return render(request, 'members/lista_donaciones.html', context)


def lista_categorias(request):
    """Lista todas las categorías"""
    categorias = Categorias.objects.filter(es_activo=True)
    
    context = {
        'categorias': categorias,
    }
    return render(request, 'members/lista_categorias.html', context)