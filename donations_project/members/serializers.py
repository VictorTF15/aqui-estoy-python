from rest_framework import serializers
from .models import Usuario, Caso, Donacion

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombres', 'apellido_paterno', 'correo']

class CasoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caso
        fields = ['id', 'titulo', 'descripcion', 'fecha_creacion']

class DonacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donacion
        fields = ['id', 'monto', 'fecha', 'usuario', 'caso']