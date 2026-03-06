from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import (
    Usuarios, TipoUsuario, Casos, Donaciones,  # ✅ Cambiado de Tiposusuario a TipoUsuario
    Categorias, EstadoCaso, CasoCategorias
)


class TipoUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para tipos de usuario"""
    
    class Meta:
        model = TipoUsuario  # ✅ Cambiado
        fields = ['id', 'nombre', 'descripcion']


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para usuarios"""
    tipo_usuario = TipoUsuarioSerializer(source='id_tipo_usuario', read_only=True)
    contrasena = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Usuarios
        fields = [
            'id', 'nombres', 'apellido_paterno', 'apellido_materno',
            'correo', 'telefono', 'tipo_usuario', 'ciudad', 'estado',
            'colonia', 'direccion', 'codigo_postal', 'imagen_perfil',
            'esta_activo', 'verificado', 'fecha_registro', 'contrasena'
        ]
        read_only_fields = ['id', 'fecha_registro']
        extra_kwargs = {
            'contrasena': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Crear usuario con contraseña hasheada"""
        password = validated_data.pop('contrasena', None)
        usuario = Usuarios.objects.create(**validated_data)
        if password:
            usuario.contrasena = make_password(password)
            usuario.save()
        return usuario
    
    def update(self, instance, validated_data):
        """Actualizar usuario"""
        password = validated_data.pop('contrasena', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.contrasena = make_password(password)
        
        instance.save()
        return instance


class EstadoCasoSerializer(serializers.ModelSerializer):
    """Serializer para estados de casos"""
    
    class Meta:
        model = EstadoCaso
        fields = ['id', 'nombre', 'descripcion']


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para categorías"""
    total_casos = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Categorias
        fields = ['id', 'nombre', 'descripcion', 'es_activo', 'total_casos']


class CasoListSerializer(serializers.ModelSerializer):
    """Serializer para lista de casos (vista simplificada)"""
    beneficiario = serializers.SerializerMethodField()
    estado = EstadoCasoSerializer(source='id_estado', read_only=True)
    categorias = serializers.SerializerMethodField()
    
    class Meta:
        model = Casos
        fields = [
            'id', 'titulo', 'descripcion', 'imagen1', 'colonia',
            'beneficiario', 'estado', 'categorias', 'vistas',
            'fecha_creacion', 'esta_abierto'
        ]
    
    def get_beneficiario(self, obj):
        if obj.id_beneficiario:
            return {
                'id': obj.id_beneficiario.id,
                'nombre': f"{obj.id_beneficiario.nombres} {obj.id_beneficiario.apellido_paterno}"
            }
        return None
    
    def get_categorias(self, obj):
        caso_cats = CasoCategorias.objects.filter(id_caso=obj).select_related('id_categoria')
        return [cc.id_categoria.nombre for cc in caso_cats if cc.id_categoria]


class CasoDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle completo de caso"""
    beneficiario = UsuarioSerializer(source='id_beneficiario', read_only=True)
    estado = EstadoCasoSerializer(source='id_estado', read_only=True)
    categorias = serializers.SerializerMethodField()
    coordenadas = serializers.SerializerMethodField()
    
    class Meta:
        model = Casos
        fields = [
            'id', 'titulo', 'descripcion', 'entidad', 'colonia', 'direccion',
            'codigo_postal', 'imagen1', 'imagen2', 'imagen3', 'imagen4',
            'latitud', 'longitud', 'coordenadas', 'beneficiario', 'estado',
            'categorias', 'vistas', 'compartido', 'fecha_creacion',
            'fecha_publicacion', 'esta_abierto'  # ✅ Eliminado fecha_actualizacion
        ]
        read_only_fields = ['id', 'vistas', 'compartido', 'fecha_creacion']
    
    def get_categorias(self, obj):
        caso_cats = CasoCategorias.objects.filter(id_caso=obj).select_related('id_categoria')
        return CategoriaSerializer([cc.id_categoria for cc in caso_cats if cc.id_categoria], many=True).data
    
    def get_coordenadas(self, obj):
        if obj.latitud and obj.longitud:
            return {
                'lat': float(obj.latitud),
                'lng': float(obj.longitud)
            }
        return None


class CasoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar casos"""
    categorias = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Casos
        fields = [
            'titulo', 'descripcion', 'entidad', 'colonia', 'direccion',
            'codigo_postal', 'imagen1', 'imagen2', 'imagen3', 'imagen4',
            'latitud', 'longitud', 'categorias', 'id_estado'
        ]
    
    def create(self, validated_data):
        categorias_ids = validated_data.pop('categorias', [])
        caso = Casos.objects.create(**validated_data)
        
        # Asignar categorías
        if categorias_ids:
            for cat_id in categorias_ids:
                CasoCategorias.objects.create(
                    id_caso=caso,
                    id_categoria_id=cat_id
                )
        
        return caso
    
    def update(self, instance, validated_data):
        categorias_ids = validated_data.pop('categorias', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar categorías si se proporcionan
        if categorias_ids is not None:
            CasoCategorias.objects.filter(id_caso=instance).delete()
            for cat_id in categorias_ids:
                CasoCategorias.objects.create(
                    id_caso=instance,
                    id_categoria_id=cat_id
                )
        
        return instance


class DonacionSerializer(serializers.ModelSerializer):
    """Serializer para donaciones"""
    donador = UsuarioSerializer(source='id_donador', read_only=True)
    caso = CasoListSerializer(source='id_caso', read_only=True)
    
    class Meta:
        model = Donaciones
        fields = [
            'id', 'donador', 'caso', 'monto', 'metodo_pago',
            'referencia_pago', 'estado_donacion', 'es_anonima', 
            'mensaje_donador', 'fecha_compromiso', 'fecha_pago'
        ]
        read_only_fields = ['id', 'fecha_compromiso']


class DonacionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear donaciones"""
    
    class Meta:
        model = Donaciones
        fields = [
            'id_caso', 'monto', 'metodo_pago',
            'es_anonima', 'mensaje_donador'
        ]