from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import (
    Usuarios, TipoUsuario, Casos, Donaciones, Categorias, EstadoCaso, 
    CasoCategorias, Evidencias, Conversaciones, Mensajes, TipoMensaje,
    Reportes, EstadoReporte, Sanciones, TipoSancion, DocumentosOCR,
    EstadoOCR, LogOCR
)


# ============================================
# AUTENTICACIÓN
# ============================================

class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Serializador de inicio de sesión con correo + contraseña."""
    correo = serializers.EmailField(required=True)
    contrasena = serializers.CharField(required=False, write_only=True, style={'input_type': 'password'})
    password = serializers.CharField(required=False, write_only=True, style={'input_type': 'password'})  # compatibilidad

    class Meta:
        ref_name = 'Login'

    def validate(self, attrs):
        correo = attrs.get('correo')
        clave = attrs.get('contrasena') or attrs.get('password')

        if not clave:
            raise serializers.ValidationError({'contrasena': 'Este campo es requerido.'})

        try:
            usuario = Usuarios.objects.get(correo=correo)
        except Usuarios.DoesNotExist:
            raise serializers.ValidationError({'detail': 'Credenciales incorrectas.'})

        if not usuario.esta_activo:
            raise serializers.ValidationError({'detail': 'La cuenta está inactiva.'})

        if not usuario.check_password(clave):
            raise serializers.ValidationError({'detail': 'Credenciales incorrectas.'})

        refresh = RefreshToken.for_user(usuario)
        refresh['correo'] = usuario.correo
        refresh['nombres'] = usuario.nombres
        refresh['tipo_usuario'] = usuario.id_tipo_usuario.nombre if usuario.id_tipo_usuario else None
        refresh['user_id'] = usuario.id

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': usuario.id,
                'correo': usuario.correo,
                'nombres': usuario.nombres,
                'apellido_paterno': usuario.apellido_paterno,
                'tipo_usuario': usuario.id_tipo_usuario.nombre if usuario.id_tipo_usuario else None,
                'imagen_perfil': usuario.imagen_perfil.url if usuario.imagen_perfil else None,
            }
        }


# ============================================
# TIPOS Y CATÁLOGOS (SOLO LECTURA)
# ============================================

class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUsuario
        fields = ['id', 'nombre', 'descripcion', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']
        ref_name = 'TipoUsuario'


class EstadoCasoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCaso
        fields = ['id', 'nombre', 'descripcion', 'es_activo']
        read_only_fields = ['id']
        ref_name = 'EstadoCaso'


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = ['id', 'nombre', 'descripcion', 'icono', 'es_activo']
        read_only_fields = ['id']
        ref_name = 'Categoria'


class TipoMensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMensaje
        fields = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']
        ref_name = 'TipoMensaje'


class EstadoReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoReporte
        fields = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']
        ref_name = 'EstadoReporte'


class TipoSancionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoSancion
        fields = ['id', 'nombre', 'descripcion', 'duracion_dias', 'es_activo']
        read_only_fields = ['id']
        ref_name = 'TipoSancion'


class EstadoOCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoOCR
        fields = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']
        ref_name = 'EstadoOCR'


# ============================================
# USUARIOS
# ============================================

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para lectura de usuarios"""
    tipo_usuario = TipoUsuarioSerializer(source='id_tipo_usuario', read_only=True)
    
    class Meta:
        model = Usuarios
        fields = [
            'id', 'nombres', 'apellido_paterno', 'apellido_materno',
            'correo', 'telefono', 'tipo_usuario',
            'ciudad', 'estado', 'colonia', 'direccion', 'codigo_postal',
            'imagen_perfil', 'esta_activo', 'verificado', 'fecha_registro',
            'imagen_ine_frontal_url', 'imagen_ine_trasera_url', 'ultimo_acceso'
        ]
        read_only_fields = ['id', 'fecha_registro', 'ultimo_acceso']
        ref_name = 'Usuario'


class UsuarioWriteSerializer(serializers.ModelSerializer):
    """Serializer para creación/actualización de usuarios"""
    contrasena = serializers.CharField(write_only=True, required=False, min_length=6)
    
    class Meta:
        model = Usuarios
        fields = [
            'nombres', 'apellido_paterno', 'apellido_materno',
            'correo', 'telefono', 'id_tipo_usuario', 'ciudad', 'estado',
            'colonia', 'direccion', 'codigo_postal', 'contrasena',
            'imagen_perfil', 'imagen_ine_frontal_url', 'imagen_ine_trasera_url'
        ]
        extra_kwargs = {
            'contrasena': {'required': False}
        }
        ref_name = 'UsuarioWrite'
    
    def create(self, validated_data):
        password = validated_data.pop('contrasena', None)
        usuario = Usuarios.objects.create(**validated_data)
        if password:
            usuario.contrasena = make_password(password)
            usuario.save()
        return usuario
    
    def update(self, instance, validated_data):
        password = validated_data.pop('contrasena', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.contrasena = make_password(password)
        instance.save()
        return instance


# ============================================
# CASOS
# ============================================

class CasoSerializer(serializers.ModelSerializer):
    """Serializer para lectura de casos"""
    beneficiario = UsuarioSerializer(source='id_beneficiario', read_only=True)
    estado = EstadoCasoSerializer(source='id_estado', read_only=True)
    categorias = serializers.SerializerMethodField()
    
    class Meta:
        model = Casos
        fields = [
            'id', 'titulo', 'descripcion', 'colonia', 'entidad',
            'latitud', 'longitud', 'esta_abierto', 'prioridad',
            'vistas', 'beneficiario', 'estado', 'categorias',
            'fecha_creacion', 'fecha_publicacion', 'fecha_conclusion',
            'imagen1', 'imagen2', 'imagen3', 'imagen4'
        ]
        read_only_fields = ['id', 'vistas', 'fecha_creacion']
        ref_name = 'Caso'
    
    def get_categorias(self, obj):
        return [cc.id_categoria.nombre for cc in obj.casocategorias_set.all()]


class CasoWriteSerializer(serializers.ModelSerializer):
    """Serializer para creación/actualización de casos"""
    categorias_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Casos
        fields = [
            'titulo', 'descripcion', 'colonia', 'entidad',
            'latitud', 'longitud', 'prioridad',
            'id_beneficiario', 'id_estado', 'categorias_ids',
            'imagen1', 'imagen2', 'imagen3', 'imagen4'
        ]
        ref_name = 'CasoWrite'
    
    def create(self, validated_data):
        categorias_ids = validated_data.pop('categorias_ids', [])
        caso = Casos.objects.create(**validated_data)
        
        for cat_id in categorias_ids:
            CasoCategorias.objects.create(
                id_caso=caso,
                id_categoria_id=cat_id
            )
        
        return caso


# ============================================
# RELACIONES
# ============================================

class CasoCategoriaSerializer(serializers.ModelSerializer):
    caso_titulo = serializers.CharField(source='id_caso.titulo', read_only=True)
    categoria = CategoriaSerializer(source='id_categoria', read_only=True)
    
    class Meta:
        model = CasoCategorias
        fields = ['id', 'caso_titulo', 'categoria', 'id_caso', 'id_categoria', 'fecha_asignacion']
        read_only_fields = ['id', 'fecha_asignacion']
        ref_name = 'CasoCategoria'


# ============================================
# DONACIONES
# ============================================

class DonacionSerializer(serializers.ModelSerializer):
    donador = UsuarioSerializer(source='id_donador', read_only=True)
    caso_titulo = serializers.CharField(source='id_caso.titulo', read_only=True)
    
    class Meta:
        model = Donaciones
        fields = [
            'id', 'monto', 'estado_donacion', 'metodo_pago',
            'donador', 'caso_titulo', 'id_donador', 'id_caso',
            'fecha_compromiso', 'fecha_pago', 'es_anonima',
            'mensaje_donador'
        ]
        read_only_fields = ['id']
        ref_name = 'Donacion'


# ============================================
# EVIDENCIAS
# ============================================

class EvidenciaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(source='id_usuario', read_only=True)
    caso = serializers.StringRelatedField(source='id_caso', read_only=True)
    
    class Meta:
        model = Evidencias
        fields = [
            'id', 'titulo', 'descripcion', 'tipo_archivo',
            'ruta_archivo', 'usuario', 'caso', 'id_usuario',
            'id_caso', 'fecha_creacion', 'es_publico',
            'imagen1', 'imagen2'
        ]
        read_only_fields = ['id', 'fecha_creacion']
        ref_name = 'Evidencia'


# ============================================
# MENSAJERÍA
# ============================================

class MensajeSerializer(serializers.ModelSerializer):
    emisor_nombre = serializers.CharField(source='id_emisor.nombres', read_only=True)
    tipo = TipoMensajeSerializer(source='id_tipo', read_only=True)
    
    class Meta:
        model = Mensajes
        fields = [
            'id', 'contenido', 'es_leido', 'emisor_nombre', 'tipo',
            'id_conversacion', 'id_emisor', 'id_tipo',
            'fecha_envio', 'fecha_leido', 'adjunto'
        ]
        read_only_fields = ['id', 'fecha_envio']
        ref_name = 'Mensaje'


class ConversacionSerializer(serializers.ModelSerializer):
    usuario1_nombre = serializers.CharField(source='id_usuario1.nombres', read_only=True)
    usuario2_nombre = serializers.CharField(source='id_usuario2.nombres', read_only=True)
    caso = serializers.StringRelatedField(source='id_caso', read_only=True)
    
    class Meta:
        model = Conversaciones
        fields = [
            'id', 'usuario1_nombre', 'usuario2_nombre', 'caso',
            'id_usuario1', 'id_usuario2', 'id_caso',
            'fecha_creacion', 'esta_activa'
        ]
        read_only_fields = ['id', 'fecha_creacion']
        ref_name = 'Conversacion'


# ============================================
# REPORTES Y SANCIONES
# ============================================

class ReporteSerializer(serializers.ModelSerializer):
    usuario_reportado_nombre = serializers.CharField(source='id_usuario_reportado.nombres', read_only=True)
    usuario_reporte_nombre = serializers.CharField(source='id_usuario_reporte.nombres', read_only=True)
    estado = EstadoReporteSerializer(source='id_estado', read_only=True)
    
    class Meta:
        model = Reportes
        fields = [
            'id', 'titulo', 'descripcion',
            'usuario_reportado_nombre', 'usuario_reporte_nombre', 'estado',
            'id_usuario_reportado', 'id_usuario_reporte', 'id_estado', 'id_caso',
            'evidencia1', 'evidencia2', 'evidencia3',
            'fecha_creacion', 'fecha_resolucion', 'resolucion'
        ]
        read_only_fields = ['id', 'fecha_creacion']
        ref_name = 'Reporte'


class SancionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='id_usuario.nombres', read_only=True)
    tipo = TipoSancionSerializer(source='id_tipo_sancion', read_only=True)
    
    class Meta:
        model = Sanciones
        fields = [
            'id', 'motivo', 'es_activa',
            'usuario_nombre', 'tipo', 'id_usuario', 'id_tipo_sancion', 'id_reporte',
            'fecha_inicio', 'fecha_fin'
        ]
        read_only_fields = ['id']
        ref_name = 'Sancion'


# ============================================
# OCR
# ============================================

class DocumentoOCRSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='id_usuario.nombres', read_only=True)
    estado = EstadoOCRSerializer(source='id_estado', read_only=True)
    validado_por_nombre = serializers.CharField(source='validado_por.nombres', read_only=True)
    
    class Meta:
        model = DocumentosOCR
        fields = [
            'id', 'tipo_documento', 'id_relacionado', 'ruta_imagen',
            'intentos_procesamiento',
            'nombre_extraido', 'apellido_paterno_extraido', 'apellido_materno_extraido',
            'curp_extraida', 'clave_electoral_extraida', 'cic_extraido', 'ocr_id_cr_extraido',
            'fecha_nacimiento_extraida', 'sexo_extraido', 'direccion_extraida', 'vigencia_extraida',
            'confianza_ocr', 'datos_validados', 'fecha_validacion', 'notas_validacion',
            'respuesta_ocr_completa',
            'usuario_nombre', 'estado', 'validado_por_nombre',
            'id_usuario', 'id_estado', 'validado_por',
            'fecha_subida', 'fecha_procesamiento'
        ]
        read_only_fields = ['id', 'fecha_subida', 'fecha_procesamiento']
        ref_name = 'DocumentoOCR'


class DocumentoOCRUploadSerializer(serializers.Serializer):
    archivo_frontal = serializers.ImageField(required=False)
    archivo_trasera = serializers.ImageField(required=False)
    id_relacionado = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        if not attrs.get('archivo_frontal') and not attrs.get('archivo_trasera'):
            raise serializers.ValidationError('Debes enviar al menos archivo_frontal o archivo_trasera.')
        return attrs

    class Meta:
        ref_name = 'DocumentoOCRUpload'


class DocumentoOCRProcessResponseSerializer(serializers.Serializer):
    documentos = DocumentoOCRSerializer(many=True)
    resumen = serializers.DictField()

    class Meta:
        ref_name = 'DocumentoOCRProcessResponse'


class LogOCRSerializer(serializers.ModelSerializer):
    estado_anterior_nombre = serializers.CharField(source='estado_anterior.nombre', read_only=True)
    estado_nuevo_nombre = serializers.CharField(source='estado_nuevo.nombre', read_only=True)
    
    class Meta:
        model = LogOCR
        fields = [
            'id', 'id_documento_ocr', 
            'estado_anterior_nombre', 'estado_nuevo_nombre',
            'mensaje', 'error_detalle', 'tiempo_procesamiento_ms', 'fecha_evento'
        ]
        read_only_fields = ['id', 'fecha_evento']
        ref_name = 'LogOCR'