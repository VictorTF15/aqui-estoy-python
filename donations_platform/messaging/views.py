from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversacion, Mensaje
from .forms import MensajeForm

@login_required
def conversaciones_view(request):
    conversaciones = Conversacion.objects.filter(participantes=request.user)
    return render(request, 'messaging/conversaciones.html', {'conversaciones': conversaciones})

@login_required
def hilo_mensajes_view(request, conversacion_id):
    conversacion = Conversacion.objects.get(id=conversacion_id)
    mensajes = Mensaje.objects.filter(conversacion=conversacion).order_by('fecha_envio')
    
    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.emisor = request.user
            mensaje.conversacion = conversacion
            mensaje.save()
            return redirect('messaging:hilo_mensajes', conversacion_id=conversacion.id)
    else:
        form = MensajeForm()

    return render(request, 'messaging/hilo_mensajes.html', {
        'conversacion': conversacion,
        'mensajes': mensajes,
        'form': form
    })