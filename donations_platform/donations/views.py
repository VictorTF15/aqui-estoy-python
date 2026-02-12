from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Donaciones, Casos
from .forms import DonacionForm

@login_required
def lista_donaciones(request):
    donaciones = Donaciones.objects.filter(id_donador=request.user)
    return render(request, 'donations/lista_donaciones.html', {'donaciones': donaciones})

@login_required
def crear_donacion(request, caso_id):
    caso = Casos.objects.get(id=caso_id)
    if request.method == 'POST':
        form = DonacionForm(request.POST)
        if form.is_valid():
            donacion = form.save(commit=False)
            donacion.id_donador = request.user
            donacion.id_caso = caso
            donacion.save()
            messages.success(request, 'Donación creada exitosamente.')
            return redirect('donations:lista_donaciones')
    else:
        form = DonacionForm()
    return render(request, 'donations/crear_donacion.html', {'form': form, 'caso': caso})