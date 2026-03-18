from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UsuariosManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El correo electrónico es obligatorio')
        
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('esta_activo', True)
        
        return self.create_user(correo, password, **extra_fields)


class TipoUsuario(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tipo_usuario'
        verbose_name = 'Tipo de Usuario'
        verbose_name_plural = 'Tipos de Usuario'

    def __str__(self):
        return self.nombre


class Usuarios(AbstractBaseUser, PermissionsMixin):
    nombres = models.CharField(max_length=255)
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255, blank=True, null=True)
    correo = models.EmailField(max_length=255, unique=True)
    contrasena = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    id_tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.PROTECT, null=True)
    ciudad = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=255, blank=True, null=True)
    colonia = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    imagen_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    esta_activo = models.BooleanField(default=True)
    verificado = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    imagen_ine_frontal_url = models.CharField(max_length=500, blank=True, null=True)
    imagen_ine_trasera_url = models.CharField(max_length=500, blank=True, null=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    
    # Campos requeridos por Django Admin
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    objects = UsuariosManager()
    
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombres', 'apellido_paterno']
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno}"
    
    # Sobrescribir métodos de password para usar el campo 'contrasena'
    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.contrasena = make_password(raw_password)
        self._password = raw_password
    
    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.contrasena)
    
    @property
    def password(self):
        return self.contrasena
    
    @password.setter
    def password(self, value):
        self.contrasena = value


class TipoMensaje(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'TipoMensaje'
        verbose_name_plural = 'Tipos de Mensaje'

    def __str__(self):
        return self.nombre


class EstadoCaso(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    es_activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'EstadoCaso'
        verbose_name_plural = 'Estados de Caso'

    def __str__(self):
        return self.nombre


class EstadoReporte(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'EstadoReporte'
        verbose_name_plural = 'Estados de Reporte'

    def __str__(self):
        return self.nombre


class TipoSancion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    duracion_dias = models.IntegerField(null=True, blank=True)
    es_activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'TipoSancion'
        verbose_name_plural = 'Tipos de Sanción'

    def __str__(self):
        return self.nombre


class EstadoOCR(models.Model):
    nombre = models.CharField(max_length=50, unique=True, help_text='Pendiente, Procesando, Exitoso, Fallido, Rechazado')
    descripcion = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'EstadoOCR'
        verbose_name_plural = 'Estados de OCR'

    def __str__(self):
        return self.nombre


class Categorias(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=300, null=True, blank=True)
    icono = models.CharField(max_length=50, null=True, blank=True)
    es_activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'Categorias'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Casos(models.Model):
    id_beneficiario = models.ForeignKey(Usuarios, on_delete=models.PROTECT, related_name='casos_beneficiario', db_column='idBeneficiario')
    id_estado = models.ForeignKey(EstadoCaso, on_delete=models.PROTECT, db_column='idEstado')
    esta_abierto = models.BooleanField(default=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    entidad = models.CharField(max_length=100, null=True, blank=True)
    direccion = models.CharField(max_length=300, null=True, blank=True)
    colonia = models.CharField(max_length=100, null=True, blank=True)
    codigo_postal = models.CharField(max_length=10, null=True, blank=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    fecha_conclusion = models.DateTimeField(null=True, blank=True)
    fecha_limite = models.DateTimeField(null=True, blank=True)
    imagen1 = models.CharField(max_length=500, null=True, blank=True)
    imagen2 = models.CharField(max_length=500, null=True, blank=True)
    imagen3 = models.CharField(max_length=500, null=True, blank=True)
    imagen4 = models.CharField(max_length=500, null=True, blank=True)
    vistas = models.IntegerField(default=0)
    compartido = models.IntegerField(default=0)
    prioridad = models.IntegerField(default=0)

    class Meta:
        db_table = 'Casos'
        verbose_name_plural = 'Casos'
        indexes = [
            models.Index(fields=['id_estado']),
            models.Index(fields=['id_beneficiario']),
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['latitud', 'longitud']),
        ]

    def __str__(self):
        return self.titulo


class CasoCategorias(models.Model):
    id_caso = models.ForeignKey(Casos, on_delete=models.CASCADE, db_column='idCaso')
    id_categoria = models.ForeignKey(Categorias, on_delete=models.PROTECT, db_column='idCategoria')
    fecha_asignacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'CasoCategorias'
        verbose_name_plural = 'Caso Categorías'
        unique_together = [['id_caso', 'id_categoria']]
        indexes = [
            models.Index(fields=['id_caso']),
            models.Index(fields=['id_categoria']),
        ]

    def __str__(self):
        return f"{self.id_caso} - {self.id_categoria}"


class Evidencias(models.Model):
    id_caso = models.ForeignKey(Casos, on_delete=models.CASCADE, db_column='idCaso')
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.PROTECT, db_column='idUsuario')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(null=True, blank=True)
    tipo_archivo = models.CharField(max_length=20, null=True, blank=True)
    ruta_archivo = models.CharField(max_length=500)
    imagen1 = models.CharField(max_length=500, null=True, blank=True)
    imagen2 = models.CharField(max_length=500, null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    es_publico = models.BooleanField(default=True)

    class Meta:
        db_table = 'Evidencias'
        verbose_name_plural = 'Evidencias'
        indexes = [
            models.Index(fields=['id_caso']),
        ]

    def __str__(self):
        return self.titulo


class Donaciones(models.Model):
    id_donador = models.ForeignKey(Usuarios, on_delete=models.PROTECT, related_name='donaciones_realizadas', db_column='idDonador')
    id_caso = models.ForeignKey(Casos, on_delete=models.PROTECT, db_column='idCaso')
    cantidad_donacion = models.DecimalField(max_digits=10, decimal_places=2, db_column='cantidadDonacion', null=True, blank=True)
    descripcion_donacion = models.TextField(db_column='descripcionDonacion', null=True, blank=True)
    id_categoria = models.ForeignKey(Categorias, on_delete=models.PROTECT, db_column='idCategoria', null=True, blank=True)    
    fecha_compromiso = models.DateTimeField(default=timezone.now)
    fecha_donacion = models.DateTimeField(null=True, blank=True)
    estado_donacion = models.CharField(max_length=50, default='Pendiente')
    mensaje_donador = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'Donaciones'
        verbose_name_plural = 'Donaciones'
        indexes = [
            models.Index(fields=['id_caso']),
            models.Index(fields=['id_donador']),
            models.Index(fields=['fecha_compromiso']),
            models.Index(fields=['id_categoria']),
        ]

    def __str__(self):
        return f"Donación al caso {self.id_caso}"


class Conversaciones(models.Model):
    id_caso = models.ForeignKey(Casos, on_delete=models.PROTECT, null=True, blank=True, db_column='idCaso')
    id_usuario1 = models.ForeignKey(Usuarios, on_delete=models.PROTECT, related_name='conversaciones_usuario1', db_column='idUsuario1')
    id_usuario2 = models.ForeignKey(Usuarios, on_delete=models.PROTECT, related_name='conversaciones_usuario2', db_column='idUsuario2')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    esta_activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'Conversaciones'
        verbose_name_plural = 'Conversaciones'
        unique_together = [['id_usuario1', 'id_usuario2', 'id_caso']]
        indexes = [
            models.Index(fields=['id_usuario1', 'id_usuario2']),
        ]

    def __str__(self):
        return f"Conversación entre {self.id_usuario1} y {self.id_usuario2}"


class Mensajes(models.Model):
    id_conversacion = models.ForeignKey(Conversaciones, on_delete=models.CASCADE, db_column='idConversacion')
    id_emisor = models.ForeignKey(Usuarios, on_delete=models.PROTECT, db_column='idEmisor')
    id_tipo = models.ForeignKey(TipoMensaje, on_delete=models.PROTECT, db_column='idTipo')
    contenido = models.TextField()
    adjunto = models.CharField(max_length=500, null=True, blank=True)
    fecha_envio = models.DateTimeField(default=timezone.now)
    fecha_leido = models.DateTimeField(null=True, blank=True)
    es_leido = models.BooleanField(default=False)
    es_eliminado = models.BooleanField(default=False)

    class Meta:
        db_table = 'Mensajes'
        verbose_name_plural = 'Mensajes'
        indexes = [
            models.Index(fields=['id_conversacion']),
            models.Index(fields=['id_emisor']),
        ]

    def __str__(self):
        return f"Mensaje de {self.id_emisor} en {self.id_conversacion}"


class Reportes(models.Model):
    id_usuario_reportado = models.ForeignKey(Usuarios, on_delete=models.PROTECT, related_name='reportes_recibidos', db_column='idUsuarioReportado')
    id_usuario_reporte = models.ForeignKey(Usuarios, on_delete=models.PROTECT, related_name='reportes_realizados', db_column='idUsuarioReporte')
    id_caso = models.ForeignKey(Casos, on_delete=models.PROTECT, null=True, blank=True, db_column='idCaso')
    id_estado = models.ForeignKey(EstadoReporte, on_delete=models.PROTECT, db_column='idEstado')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    evidencia1 = models.CharField(max_length=500, null=True, blank=True)
    evidencia2 = models.CharField(max_length=500, null=True, blank=True)
    evidencia3 = models.CharField(max_length=500, null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resolucion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'Reportes'
        verbose_name_plural = 'Reportes'
        indexes = [
            models.Index(fields=['id_usuario_reportado']),
            models.Index(fields=['id_estado']),
        ]

    def __str__(self):
        return self.titulo


class Sanciones(models.Model):
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.PROTECT, db_column='idUsuario')
    id_reporte = models.ForeignKey(Reportes, on_delete=models.PROTECT, db_column='idReporte')
    id_tipo_sancion = models.ForeignKey(TipoSancion, on_delete=models.PROTECT, db_column='idTipoSancion')
    motivo = models.TextField()
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    es_activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'Sanciones'
        verbose_name_plural = 'Sanciones'
        indexes = [
            models.Index(fields=['id_usuario']),
        ]

    def __str__(self):
        return f"Sanción {self.id_tipo_sancion} a {self.id_usuario}"


class DocumentosOCR(models.Model):
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.PROTECT, db_column='idUsuario')
    tipo_documento = models.CharField(max_length=50, help_text='INE_FRONTAL, INE_TRASERA, COMPROBANTE_DOMICILIO, EVIDENCIA_CASO')
    id_relacionado = models.IntegerField(null=True, blank=True, help_text='ID del caso o evidencia relacionada')
    ruta_imagen = models.CharField(max_length=500)
    id_estado = models.ForeignKey(EstadoOCR, on_delete=models.PROTECT, db_column='idEstado')
    fecha_subida = models.DateTimeField(default=timezone.now)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    intentos_procesamiento = models.IntegerField(default=0)
    
    nombre_extraido = models.CharField(max_length=200, null=True, blank=True)
    apellido_paterno_extraido = models.CharField(max_length=100, null=True, blank=True)
    apellido_materno_extraido = models.CharField(max_length=100, null=True, blank=True)
    curp_extraida = models.CharField(max_length=18, null=True, blank=True)
    clave_electoral_extraida = models.CharField(max_length=18, null=True, blank=True)
    cic_extraido = models.CharField(max_length=9, null=True, blank=True)
    ocr_id_cr_extraido = models.CharField(max_length=13, null=True, blank=True)
    fecha_nacimiento_extraida = models.DateField(null=True, blank=True)
    sexo_extraido = models.CharField(max_length=1, null=True, blank=True)
    direccion_extraida = models.CharField(max_length=300, null=True, blank=True)
    vigencia_extraida = models.CharField(max_length=10, null=True, blank=True)
    
    confianza_ocr = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Porcentaje de confianza del OCR (0-100)')
    datos_validados = models.BooleanField(default=False)
    validado_por = models.ForeignKey(Usuarios, on_delete=models.PROTECT, null=True, blank=True, related_name='validaciones_ocr', db_column='validadoPor')
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    notas_validacion = models.TextField(null=True, blank=True)
    
    respuesta_ocr_completa = models.JSONField(null=True, blank=True, help_text='Respuesta completa del servicio OCR')

    class Meta:
        db_table = 'DocumentosOCR'
        verbose_name_plural = 'Documentos OCR'
        indexes = [
            models.Index(fields=['id_usuario']),
            models.Index(fields=['id_estado']),
            models.Index(fields=['tipo_documento']),
            models.Index(fields=['fecha_subida']),
        ]

    def __str__(self):
        return f"{self.tipo_documento} - {self.id_usuario}"


class LogOCR(models.Model):
    id_documento_ocr = models.ForeignKey(DocumentosOCR, on_delete=models.CASCADE, db_column='idDocumentoOCR')
    estado_anterior = models.ForeignKey(EstadoOCR, on_delete=models.PROTECT, null=True, blank=True, related_name='logs_estado_anterior', db_column='estadoAnterior')
    estado_nuevo = models.ForeignKey(EstadoOCR, on_delete=models.PROTECT, related_name='logs_estado_nuevo', db_column='estadoNuevo')
    mensaje = models.TextField(null=True, blank=True)
    error_detalle = models.TextField(null=True, blank=True)
    tiempo_procesamiento_ms = models.IntegerField(null=True, blank=True)
    fecha_evento = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'LogOCR'
        verbose_name_plural = 'Logs OCR'
        indexes = [
            models.Index(fields=['id_documento_ocr']),
            models.Index(fields=['fecha_evento']),
        ]

    def __str__(self):
        return f"Log OCR {self.id_documento_ocr} - {self.fecha_evento}"