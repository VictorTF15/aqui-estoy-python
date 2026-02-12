from django.shortcuts import render, get_object_or_404
from .models import Usuario, Caso, Historial

def feed(request):
    usuario = get_object_or_404(Usuario, id=request.user.id)
    casos_recientes = Caso.objects.order_by('-fecha_creacion')[:5]
    historial = Historial.objects.filter(usuario=usuario).order_by('-fecha')[:10]
    
    context = {
        'usuario': usuario,
        'casos_recientes': casos_recientes,
        'historial': historial,
    }
    
    return render(request, 'members/feed.html', context)

def lista_casos(request):
    casos = Caso.objects.all()
    return render(request, 'members/lista_casos.html', {'casos': casos})

def detalle_caso(request, caso_id):
    caso = get_object_or_404(Caso, id=caso_id)
    return render(request, 'members/detalle_caso.html', {'caso': caso})

def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'members/lista_usuarios.html', {'usuarios': usuarios})

def perfil_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'members/perfil_usuario.html', {'usuario': usuario})

def lista_donaciones(request):
    # Assuming there's a Donacion model
    donaciones = Donacion.objects.all()
    return render(request, 'members/lista_donaciones.html', {'donaciones': donaciones})

def lista_categorias(request):
    # Assuming there's a Categoria model
    categorias = Categoria.objects.all()
    return render(request, 'members/lista_categorias.html', {'categorias': categorias})