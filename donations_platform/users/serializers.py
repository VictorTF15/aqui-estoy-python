from rest_framework import serializers
from .models import Usuarios, Donaciones

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ['id', 'nombres', 'apellido_paterno', 'apellido_materno', 'correo', 'telefono', 'ciudad', 'estado', 'fecha_registro']

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donaciones
        fields = ['id', 'id_donador', 'id_caso', 'monto', 'metodo_pago', 'fecha_compromiso', 'estado_donacion']