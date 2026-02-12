from django import forms
from .models import TipoUsuario, EstadoCaso

class RegistrationForm(forms.Form):
    nombres = forms.CharField(max_length=150, required=True)
    apellido_paterno = forms.CharField(max_length=150, required=True)
    apellido_materno = forms.CharField(max_length=150, required=False)
    correo = forms.EmailField(required=True)
    contrasena = forms.CharField(required=True, widget=forms.PasswordInput)
    tipo = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tipos = TipoUsuario.objects.all()
        choices = [('', 'Seleccionar (opcional)')] + [(t.nombre, t.nombre) for t in tipos]
        self.fields['tipo'].choices = choices


class CasoForm(forms.Form):
    titulo = forms.CharField(max_length=250, required=True)
    descripcion = forms.CharField(widget=forms.Textarea, required=False)
    imagen1 = forms.URLField(required=False)
    imagen2 = forms.URLField(required=False)
    imagen3 = forms.URLField(required=False)
    imagen4 = forms.URLField(required=False)
    estado = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        estados = EstadoCaso.objects.all()
        self.fields['estado'].choices = [('', 'Por defecto (Abierto)')] + [(e.nombre, e.nombre) for e in estados]