from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import (
    Usuarios, TipoUsuario, Casos, Donaciones, Categorias, EstadoCaso, 
    CasoCategorias, Evidencias, Conversaciones, Mensajes, TipoMensaje,
    Reportes, EstadoReporte, Sanciones, TipoSancion, DocumentosOCR,
    EstadoOCR, LogOCR
)


class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUsuario  
        fields = ['id', 'nombre', 'descripcion', 'fecha_creacion']


class UsuarioListSerializer(serializers.ModelSerializer):
    tipo_usuario = serializers.CharField(source='id_tipo_usuario.nombre', read_only=True)
    
    class Meta:
        model = Usuarios
        fields = [
            'id', 'nombres', 'apellido_paterno', 'apellido_materno',
            'correo', 'telefono', 'tipo_usuario', 'ciudad', 'estado',
            'esta_activo', 'verificado', 'fecha_registro'
        ]


class UsuarioDetailSerializer(serializers.ModelSerializer):
    tipo_usuario = TipoUsuarioSerializer(source='id_tipo_usuario', read_only=True)
    
    class Meta:
        model = Usuarios
        fields = [
            'id', 'nombres', 'apellido_paterno', 'apellido_materno',
            'correo', 'telefono', 'tipo_usuario', 'ciudad', 'estado',
            'colonia', 'direccion', 'codigo_postal', 'imagen_perfil',
            'esta_activo', 'verificado', 'fecha_registro',
            'imagen_ine_frontal_url', 'imagen_ine_trasera_url', 'ultimo_acceso'
        ]
        read_only_fields = ['id', 'fecha_registro', 'ultimo_acceso']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = [
            'nombres', 'apellido_paterno', 'apellido_materno',
            'correo', 'telefono', 'id_tipo_usuario', 'ciudad', 'estado',
            'colonia', 'direccion', 'codigo_postal', 'contrasena',
            'imagen_perfil', 'imagen_ine_frontal_url', 'imagen_ine_trasera_url'
        ]
        extra_kwargs = {
            'contrasena': {'write_only': True, 'required': True},
            'colonia': {'required': False},
            'direccion': {'required': False},
            'codigo_postal': {'required': False},
            'imagen_perfil': {'required': False},
            'imagen_ine_frontal_url': {'required': False},
            'imagen_ine_trasera_url': {'required': False}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('contrasena')
        usuario = Usuarios.objects.create(**validated_data)
        usuario.contrasena = make_password(password)
        usuario.save()
        return usuario


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    contrasena = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Usuarios
        fields = [
            'nombres', 'apellido_paterno', 'apellido_materno',
            'telefono', 'ciudad', 'estado', 'colonia', 'direccion',
            'codigo_postal', 'imagen_perfil', 'contrasena'
        ]
        extra_kwargs = {
            'nombres': {'required': False},
            'apellido_paterno': {'required': False},
            'apellido_materno': {'required': False},
            'telefono': {'required': False},
            'ciudad': {'required': False},
            'estado': {'required': False},
        }
    
    def update(self, instance, validated_data):
        password = validated_data.pop('contrasena', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.contrasena = make_password(password)
        instance.save()
        return instance


class CambiarContrasenaSerializer(serializers.Serializer):
    contrasena_actual = serializers.CharField(write_only=True, required=True)
    contrasena_nueva = serializers.CharField(write_only=True, required=True, min_length=8)
    confirmar_contrasena = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        if data['contrasena_nueva'] != data['confirmar_contrasena']:
            raise serializers.ValidationError({"confirmar_contrasena": "Las contraseñas no coinciden"})
        return data


class ActualizarTelefonoSerializer(serializers.Serializer):
    telefono = serializers.CharField(max_length=15, required=True)


class AsignarTipoUsuarioSerializer(serializers.Serializer):
    id_tipo_usuario = serializers.IntegerField(required=True)


class EstadoCasoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCaso
        fields = ['id', 'nombre', 'descripcion', 'es_activo']


class CategoriaSerializer(serializers.ModelSerializer):
    total_casos = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Categorias
        fields = ['id', 'nombre', 'descripcion', 'icono', 'es_activo', 'total_casos']


class CasoListSerializer(serializers.ModelSerializer):
    beneficiario = serializers.SerializerMethodField()
    estado = EstadoCasoSerializer(source='id_estado', read_only=True)
    categorias = serializers.SerializerMethodField()
    
    class Meta:
        model = Casos
        fields = [
            'id', 'titulo', 'descripcion', 'imagen1', 'colonia',
            'beneficiario', 'estado', 'categorias', 'vistas',
            'fecha_creacion', 'esta_abierto', 'prioridad'
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
    beneficiario = UsuarioDetailSerializer(source='id_beneficiario', read_only=True)
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
            'fecha_publicacion', 'fecha_conclusion', 'fecha_limite',
            'esta_abierto', 'prioridad'
        ]
        read_only_fields = ['id', 'vistas', 'compartido', 'fecha_creacion']
    
    def get_categorias(self, obj):
        caso_cats = CasoCategorias.objects.filter(id_caso=obj).select_related('id_categoria')
        return CategoriaSerializer([cc.id_categoria for cc in caso_cats if cc.id_categoria], many=True).data
    
    def get_coordenadas(self, obj):
        if obj.latitud and obj.longitud:
            return {'lat': float(obj.latitud), 'lng': float(obj.longitud)}
        return None


class CasoCreateUpdateSerializer(serializers.ModelSerializer):
    categorias = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Lista de IDs de categorías"
    )
    
    class Meta:
        model = Casos
        fields = [
            'titulo', 'descripcion', 'entidad', 'colonia', 'direccion',
            'codigo_postal', 'imagen1', 'imagen2', 'imagen3', 'imagen4',
            'latitud', 'longitud', 'categorias', 'id_estado', 'fecha_limite',
            'prioridad', 'id_beneficiario'
        ]
        extra_kwargs = {
            'imagen2': {'required': False},
            'imagen3': {'required': False},
            'imagen4': {'required': False},
            'latitud': {'required': False},
            'longitud': {'required': False},
            'categorias': {'required': False},
            'id_estado': {'required': False},
            'fecha_limite': {'required': False},
            'prioridad': {'required': False},
        }
    
    def create(self, validated_data):
        categorias_ids = validated_data.pop('categorias', [])
        caso = Casos.objects.create(**validated_data)
        if categorias_ids:
            for cat_id in categorias_ids:
                CasoCategorias.objects.create(id_caso=caso, id_categoria_id=cat_id)
        return caso
    
    def update(self, instance, validated_data):
        categorias_ids = validated_data.pop('categorias', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if categorias_ids is not None:
            CasoCategorias.objects.filter(id_caso=instance).delete()
            for cat_id in categorias_ids:
                CasoCategorias.objects.create(id_caso=instance, id_categoria_id=cat_id)
        return instance


class CasoCategoriaSerializer(serializers.ModelSerializer):
    caso = CasoListSerializer(source='id_caso', read_only=True)
    categoria = CategoriaSerializer(source='id_categoria', read_only=True)
    
    class Meta:
        model = CasoCategorias
        fields = ['id', 'caso', 'categoria', 'fecha_asignacion']
        read_only_fields = ['fecha_asignacion']


class DonacionSerializer(serializers.ModelSerializer):
    donador = UsuarioListSerializer(source='id_donador', read_only=True)
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
    class Meta:
        model = Donaciones
        fields = ['id_caso', 'monto', 'metodo_pago', 'es_anonima', 'mensaje_donador']
        extra_kwargs = {
            'es_anonima': {'required': False, 'default': False},
            'mensaje_donador': {'required': False, 'allow_blank': True}
        }


class EvidenciaSerializer(serializers.ModelSerializer):
    caso = CasoListSerializer(source='id_caso', read_only=True)
    usuario = UsuarioListSerializer(source='id_usuario', read_only=True)
    
    class Meta:
        model = Evidencias
        fields = [
            'id', 'caso', 'usuario', 'titulo', 'descripcion', 'tipo_archivo',
            'ruta_archivo', 'imagen1', 'imagen2', 'fecha_creacion', 'es_publico'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class TipoMensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMensaje
        fields = ['id', 'nombre', 'descripcion']


class ConversacionSerializer(serializers.ModelSerializer):
    usuario1 = UsuarioListSerializer(source='id_usuario1', read_only=True)
    usuario2 = UsuarioListSerializer(source='id_usuario2', read_only=True)
    caso = CasoListSerializer(source='id_caso', read_only=True)
    
    class Meta:
        model = Conversaciones
        fields = [
            'id', 'caso', 'usuario1', 'usuario2', 
            'fecha_creacion', 'esta_activa'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class MensajeSerializer(serializers.ModelSerializer):
    conversacion = ConversacionSerializer(source='id_conversacion', read_only=True)
    emisor = UsuarioListSerializer(source='id_emisor', read_only=True)
    tipo_mensaje = TipoMensajeSerializer(source='id_tipo', read_only=True)
    
    class Meta:
        model = Mensajes
        fields = [
            'id', 'conversacion', 'emisor', 'tipo_mensaje', 'contenido',
            'adjunto', 'fecha_envio', 'fecha_leido', 'es_leido', 'es_eliminado'
        ]
        read_only_fields = ['id', 'fecha_envio', 'fecha_leido']


class EstadoReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoReporte
        fields = ['id', 'nombre', 'descripcion']


class ReporteSerializer(serializers.ModelSerializer):
    usuario_reportado = UsuarioListSerializer(source='id_usuario_reportado', read_only=True)
    usuario_reporte = UsuarioListSerializer(source='id_usuario_reporte', read_only=True)
    caso = CasoListSerializer(source='id_caso', read_only=True)
    estado = EstadoReporteSerializer(source='id_estado', read_only=True)
    
    class Meta:
        model = Reportes
        fields = [
            'id', 'usuario_reportado', 'usuario_reporte', 'caso', 'estado',
            'titulo', 'descripcion', 'evidencia1', 'evidencia2', 'evidencia3',
            'fecha_creacion', 'fecha_resolucion', 'resolucion'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class TipoSancionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoSancion
        fields = ['id', 'nombre', 'descripcion', 'duracion_dias', 'es_activo']


class SancionSerializer(serializers.ModelSerializer):
    usuario = UsuarioListSerializer(source='id_usuario', read_only=True)
    reporte = ReporteSerializer(source='id_reporte', read_only=True)
    tipo_sancion = TipoSancionSerializer(source='id_tipo_sancion', read_only=True)
    
    class Meta:
        model = Sanciones
        fields = [
            'id', 'usuario', 'reporte', 'tipo_sancion', 'motivo',
            'fecha_inicio', 'fecha_fin', 'es_activa'
        ]
        read_only_fields = ['id', 'fecha_inicio']


class EstadoOCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoOCR
        fields = ['id', 'nombre', 'descripcion']


class DocumentoOCRSerializer(serializers.ModelSerializer):
    usuario = UsuarioListSerializer(source='id_usuario', read_only=True)
    estado = EstadoOCRSerializer(source='id_estado', read_only=True)
    validado_por_detalle = UsuarioListSerializer(source='validado_por', read_only=True)
    
    class Meta:
        model = DocumentosOCR
        fields = [
            'id', 'usuario', 'tipo_documento', 'id_relacionado', 'ruta_imagen',
            'estado', 'fecha_subida', 'fecha_procesamiento', 'intentos_procesamiento',
            'nombre_extraido', 'apellido_paterno_extraido', 'apellido_materno_extraido',
            'curp_extraida', 'clave_electoral_extraida', 'fecha_nacimiento_extraida',
            'sexo_extraido', 'direccion_extraida', 'vigencia_extraida',
            'confianza_ocr', 'datos_validados', 'validado_por_detalle',
            'fecha_validacion', 'notas_validacion'
        ]
        read_only_fields = ['id', 'fecha_subida']


class LogOCRSerializer(serializers.ModelSerializer):
    documento = DocumentoOCRSerializer(source='id_documento_ocr', read_only=True)
    estado_anterior_detalle = EstadoOCRSerializer(source='estado_anterior', read_only=True)
    estado_nuevo_detalle = EstadoOCRSerializer(source='estado_nuevo', read_only=True)
    
    class Meta:
        model = LogOCR
        fields = [
            'id', 'documento', 'estado_anterior_detalle', 'estado_nuevo_detalle',
            'mensaje', 'error_detalle', 'tiempo_procesamiento_ms', 'fecha_evento'
        ]
        read_only_fields = ['id', 'fecha_evento']