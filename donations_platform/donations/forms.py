from django import forms
from .models import Donaciones, Casos

class DonacionForm(forms.ModelForm):
    class Meta:
        model = Donaciones
        fields = ['id_caso', 'monto', 'metodo_pago', 'referencia_pago', 'es_anonima', 'mensaje_donador']
        widgets = {
            'mensaje_donador': forms.Textarea(attrs={'rows': 3}),
        }

class CasoForm(forms.ModelForm):
    class Meta:
        model = Casos
        fields = ['titulo', 'descripcion', 'monto_objetivo', 'fecha_limite', 'imagen1', 'imagen2', 'imagen3', 'imagen4']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 5}),
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
        }