from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
import os
import re
import time
import boto3
from decouple import config

from .models import (
    Usuarios, TipoUsuario, Casos, EstadoCaso, Categorias,
    CasoCategorias, Donaciones, Evidencias, Conversaciones,
    Mensajes, TipoMensaje, Reportes, EstadoReporte,
    Sanciones, TipoSancion, DocumentosOCR, EstadoOCR, LogOCR
)

from .serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioSerializer, UsuarioWriteSerializer,
    TipoUsuarioSerializer, CasoSerializer, CasoWriteSerializer,
    EstadoCasoSerializer, CategoriaSerializer, CasoCategoriaSerializer,
    DonacionSerializer, EvidenciaSerializer, ConversacionSerializer,
    MensajeSerializer, TipoMensajeSerializer, ReporteSerializer,
    EstadoReporteSerializer, SancionSerializer, TipoSancionSerializer,
    DocumentoOCRSerializer, EstadoOCRSerializer, LogOCRSerializer,
    DocumentoOCRUploadSerializer, DocumentoOCRProcessResponseSerializer
)

@extend_schema(
    tags=['Autenticación'],
    summary='Iniciar sesión',
    description='Autentica al usuario con correo y contraseña, y devuelve tokens JWT.',
    request=CustomTokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(description='Inicio de sesión exitoso.'),
        400: OpenApiResponse(description='Credenciales inválidas o datos incompletos.'),
    }
)
class CustomTokenObtainPairView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializador = CustomTokenObtainPairSerializer(data=request.data)
        try:
            serializador.is_valid(raise_exception=True)
            return Response(serializador.validated_data, status=status.HTTP_200_OK)
        except ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {'detail': 'Error al procesar la solicitud.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================
# USUARIOS
# ============================================

@extend_schema_view(
    list=extend_schema(tags=['Usuarios'], summary='Listar usuarios', description='Obtiene la lista paginada de usuarios.'),
    create=extend_schema(tags=['Usuarios'], summary='Crear usuario', description='Crea un nuevo usuario en el sistema.'),
    retrieve=extend_schema(tags=['Usuarios'], summary='Obtener usuario', description='Obtiene el detalle de un usuario por ID.'),
    update=extend_schema(tags=['Usuarios'], summary='Actualizar usuario', description='Actualiza todos los campos de un usuario.'),
    partial_update=extend_schema(tags=['Usuarios'], summary='Actualizar parcialmente usuario', description='Actualiza solo algunos campos de un usuario.'),
    destroy=extend_schema(tags=['Usuarios'], summary='Eliminar usuario', description='Elimina un usuario del sistema.'),
)
class UsuarioViewSet(viewsets.ModelViewSet):
    """Gestión de usuarios del sistema"""
    queryset = Usuarios.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombres', 'apellido_paterno', 'apellido_materno', 'correo']
    ordering = ['-fecha_registro']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioWriteSerializer
        return UsuarioSerializer

    @extend_schema(
        tags=['Usuarios'],
        summary='Mi perfil',
        description='Devuelve los datos del usuario autenticado.'
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        tags=['Usuarios'],
        summary='Cambiar contraseña',
        description='Permite cambiar la contraseña del usuario indicado.'
    )
    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        usuario = self.get_object()
        password_actual = request.data.get('password_actual')
        password_nueva = request.data.get('password_nueva')
        
        if not usuario.check_password(password_actual):
            return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_400_BAD_REQUEST)
        
        usuario.contrasena = make_password(password_nueva)
        usuario.save()
        return Response({'message': 'Contraseña actualizada'})


@extend_schema_view(
    list=extend_schema(tags=['Catálogos'], description='Listar tipos de usuario'),
    retrieve=extend_schema(tags=['Catálogos'], description='Obtener un tipo de usuario'),
)
class TipoUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de tipos de usuario"""
    queryset = TipoUsuario.objects.all()
    serializer_class = TipoUsuarioSerializer
    permission_classes = [AllowAny]


# ============================================
# CASOS
# ============================================

@extend_schema_view(
    list=extend_schema(tags=['Casos'], summary='Listar casos', description='Obtiene la lista de casos.'),
    create=extend_schema(tags=['Casos'], summary='Crear caso', description='Crea un nuevo caso.'),
    retrieve=extend_schema(tags=['Casos'], summary='Obtener caso', description='Obtiene el detalle de un caso.'),
    update=extend_schema(tags=['Casos'], summary='Actualizar caso', description='Actualiza un caso completo.'),
    partial_update=extend_schema(tags=['Casos'], summary='Actualizar parcialmente caso', description='Actualiza campos específicos de un caso.'),
    destroy=extend_schema(tags=['Casos'], summary='Eliminar caso', description='Elimina un caso.'),
)
class CasoViewSet(viewsets.ModelViewSet):
    """Gestión de casos sociales"""
    queryset = Casos.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'descripcion', 'colonia', 'entidad']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CasoWriteSerializer
        return CasoSerializer

    @extend_schema(
        tags=['Casos'],
        summary='Casos para mapa',
        description='Devuelve solo casos abiertos con coordenadas para visualización en mapa.'
    )
    @action(detail=False, methods=['get'])
    def mapa(self, request):
        casos = self.get_queryset().filter(esta_abierto=True)
        data = [{
            'id': caso.id,
            'titulo': caso.titulo,
            'latitud': float(caso.latitud) if caso.latitud else None,
            'longitud': float(caso.longitud) if caso.longitud else None,
            'prioridad': caso.prioridad,
        } for caso in casos if caso.latitud and caso.longitud]
        return Response(data)

    @extend_schema(
        tags=['Casos'],
        summary='Estadísticas de casos',
        description='Devuelve totales de casos (total, abiertos y cerrados).'
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        return Response({
            'total': Casos.objects.count(),
            'abiertos': Casos.objects.filter(esta_abierto=True).count(),
            'cerrados': Casos.objects.filter(esta_abierto=False).count(),
        })


@extend_schema_view(
    list=extend_schema(tags=['Catálogos'], description='Listar estados de caso'),
    retrieve=extend_schema(tags=['Catálogos'], description='Obtener un estado de caso'),
)
class EstadoCasoViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de estados de caso"""
    queryset = EstadoCaso.objects.all()
    serializer_class = EstadoCasoSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['Categorías'], description='Listar categorías'),
    create=extend_schema(tags=['Categorías'], description='Crear una categoría'),
    retrieve=extend_schema(tags=['Categorías'], description='Obtener una categoría'),
    update=extend_schema(tags=['Categorías'], description='Actualizar una categoría'),
    partial_update=extend_schema(tags=['Categorías'], description='Actualizar parcialmente una categoría'),
    destroy=extend_schema(tags=['Categorías'], description='Eliminar una categoría'),
)
class CategoriaViewSet(viewsets.ModelViewSet):
    """Gestión de categorías de casos"""
    queryset = Categorias.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Casos'], description='Listar relaciones caso-categoría'),
    create=extend_schema(tags=['Casos'], description='Asignar categoría a caso'),
    retrieve=extend_schema(tags=['Casos'], description='Obtener relación caso-categoría'),
    update=extend_schema(tags=['Casos'], description='Actualizar relación caso-categoría'),
    partial_update=extend_schema(tags=['Casos'], description='Actualizar parcialmente relación'),
    destroy=extend_schema(tags=['Casos'], description='Eliminar relación caso-categoría'),
)
class CasoCategoriaViewSet(viewsets.ModelViewSet):
    """Relación entre casos y categorías"""
    queryset = CasoCategorias.objects.all()
    serializer_class = CasoCategoriaSerializer
    permission_classes = [IsAuthenticated]


# ============================================
# DONACIONES
# ============================================

@extend_schema_view(
    list=extend_schema(tags=['Donaciones'], description='Listar donaciones'),
    create=extend_schema(tags=['Donaciones'], description='Crear una donación'),
    retrieve=extend_schema(tags=['Donaciones'], description='Obtener detalles de donación'),
    update=extend_schema(tags=['Donaciones'], description='Actualizar donación'),
    partial_update=extend_schema(tags=['Donaciones'], description='Actualizar parcialmente donación'),
    destroy=extend_schema(tags=['Donaciones'], description='Eliminar donación'),
)
class DonacionViewSet(viewsets.ModelViewSet):
    """Gestión de donaciones"""
    queryset = Donaciones.objects.all()
    serializer_class = DonacionSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-fecha_compromiso']

    @extend_schema(tags=['Donaciones'], description='Obtener donaciones del usuario autenticado')
    @action(detail=False, methods=['get'])
    def mis_donaciones(self, request):
        donaciones = self.get_queryset().filter(id_donador=request.user)
        serializer = self.get_serializer(donaciones, many=True)
        return Response(serializer.data)


# ============================================
# EVIDENCIAS
# ============================================

@extend_schema_view(
    list=extend_schema(tags=['Evidencias'], description='Listar evidencias'),
    create=extend_schema(tags=['Evidencias'], description='Crear evidencia'),
    retrieve=extend_schema(tags=['Evidencias'], description='Obtener evidencia'),
    update=extend_schema(tags=['Evidencias'], description='Actualizar evidencia'),
    partial_update=extend_schema(tags=['Evidencias'], description='Actualizar parcialmente evidencia'),
    destroy=extend_schema(tags=['Evidencias'], description='Eliminar evidencia'),
)
class EvidenciaViewSet(viewsets.ModelViewSet):
    """Gestión de evidencias multimedia"""
    queryset = Evidencias.objects.all()
    serializer_class = EvidenciaSerializer
    permission_classes = [IsAuthenticated]


# ============================================
# MENSAJERÍA
# ============================================

@extend_schema_view(
    list=extend_schema(tags=['Mensajería'], description='Listar conversaciones'),
    create=extend_schema(tags=['Mensajería'], description='Crear conversación'),
    retrieve=extend_schema(tags=['Mensajería'], description='Obtener conversación'),
    update=extend_schema(tags=['Mensajería'], description='Actualizar conversación'),
    partial_update=extend_schema(tags=['Mensajería'], description='Actualizar parcialmente conversación'),
    destroy=extend_schema(tags=['Mensajería'], description='Eliminar conversación'),
)
class ConversacionViewSet(viewsets.ModelViewSet):
    """Gestión de conversaciones"""
    queryset = Conversaciones.objects.all()
    serializer_class = ConversacionSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Mensajería'], description='Listar mensajes'),
    create=extend_schema(tags=['Mensajería'], description='Enviar mensaje'),
    retrieve=extend_schema(tags=['Mensajería'], description='Obtener mensaje'),
    update=extend_schema(tags=['Mensajería'], description='Actualizar mensaje'),
    partial_update=extend_schema(tags=['Mensajería'], description='Actualizar parcialmente mensaje'),
    destroy=extend_schema(tags=['Mensajería'], description='Eliminar mensaje'),
)
class MensajeViewSet(viewsets.ModelViewSet):
    """Gestión de mensajes"""
    queryset = Mensajes.objects.all()
    serializer_class = MensajeSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-fecha_envio']


@extend_schema_view(
    list=extend_schema(tags=['Catálogos'], description='Listar tipos de mensaje'),
    retrieve=extend_schema(tags=['Catálogos'], description='Obtener tipo de mensaje'),
)
class TipoMensajeViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de tipos de mensaje"""
    queryset = TipoMensaje.objects.all()
    serializer_class = TipoMensajeSerializer
    permission_classes = [AllowAny]


# ============================================
# REPORTES Y SANCIONES
# ============================================

@extend_schema_view(
    list=extend_schema(tags=['Moderación'], description='Listar reportes'),
    create=extend_schema(tags=['Moderación'], description='Crear reporte'),
    retrieve=extend_schema(tags=['Moderación'], description='Obtener reporte'),
    update=extend_schema(tags=['Moderación'], description='Actualizar reporte'),
    partial_update=extend_schema(tags=['Moderación'], description='Actualizar parcialmente reporte'),
    destroy=extend_schema(tags=['Moderación'], description='Eliminar reporte'),
)
class ReporteViewSet(viewsets.ModelViewSet):
    """Gestión de reportes"""
    queryset = Reportes.objects.all()
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Catálogos'], description='Listar estados de reporte'),
    retrieve=extend_schema(tags=['Catálogos'], description='Obtener estado de reporte'),
)
class EstadoReporteViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de estados de reporte"""
    queryset = EstadoReporte.objects.all()
    serializer_class = EstadoReporteSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['Moderación'], description='Listar sanciones'),
    create=extend_schema(tags=['Moderación'], description='Crear sanción'),
    retrieve=extend_schema(tags=['Moderación'], description='Obtener sanción'),
    update=extend_schema(tags=['Moderación'], description='Actualizar sanción'),
    partial_update=extend_schema(tags=['Moderación'], description='Actualizar parcialmente sanción'),
    destroy=extend_schema(tags=['Moderación'], description='Eliminar sanción'),
)
class SancionViewSet(viewsets.ModelViewSet):
    """Gestión de sanciones"""
    queryset = Sanciones.objects.all()
    serializer_class = SancionSerializer
    permission_classes = [IsAdminUser]


@extend_schema_view(
    list=extend_schema(tags=['Catálogos'], description='Listar tipos de sanción'),
    retrieve=extend_schema(tags=['Catálogos'], description='Obtener tipo de sanción'),
)
class TipoSancionViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de tipos de sanción"""
    queryset = TipoSancion.objects.all()
    serializer_class = TipoSancionSerializer
    permission_classes = [AllowAny]


# ============================================
# OCR
# ============================================

@extend_schema_view(
    list=extend_schema(tags=['OCR'], description='Listar documentos OCR'),
    create=extend_schema(tags=['OCR'], description='Subir documento para OCR'),
    retrieve=extend_schema(tags=['OCR'], description='Obtener documento OCR'),
    update=extend_schema(tags=['OCR'], description='Actualizar documento OCR'),
    partial_update=extend_schema(tags=['OCR'], description='Actualizar parcialmente documento OCR'),
    destroy=extend_schema(tags=['OCR'], description='Eliminar documento OCR'),
)
class DocumentoOCRViewSet(viewsets.ModelViewSet):
    """Gestión de documentos OCR"""
    queryset = DocumentosOCR.objects.all()
    serializer_class = DocumentoOCRSerializer
    permission_classes = [IsAuthenticated]

    _CURP_REGEX = re.compile(r'[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z\d]\d')
    _CLAVE_ELECTOR_REGEX = re.compile(r'[A-Z]{6}\d{8}[HM]\d{3}')
    _CIC_REGEX = re.compile(r'IDMEX\s*(\d{9})', re.IGNORECASE)
    _CIC_FALLBACK_REGEX = re.compile(r'\b\d{9}\b')
    _OCR_ID_CR_REGEX = re.compile(r'\b\d{12,13}\b')
    _FECHA_NAC_REGEX = re.compile(r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b')
    _SEXO_REGEX = re.compile(r'\b(H|M)\b')
    _VIGENCIA_REGEX = re.compile(r'\b(\d{4})\s*[–\-]\s*(\d{4})\b')
    

    def _get_rekognition_client(self):
        AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
        AWS_REGION = "us-east-1"
        return boto3.client(
            'rekognition',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

    def _get_estado_por_nombre(self, nombre):
        return EstadoOCR.objects.get(nombre__iexact=nombre)

    def _extraer_nombre_apellidos(self, texto):
        lineas = [linea.strip() for linea in texto.split(' ') if linea.strip()]
        candidatos = [p for p in lineas if p.isalpha() and len(p) > 2]
        if not candidatos:
            return None, None, None
        nombre = candidatos[0] if len(candidatos) >= 1 else None
        apellido_paterno = candidatos[1] if len(candidatos) >= 2 else None
        apellido_materno = candidatos[2] if len(candidatos) >= 3 else None
        return nombre, apellido_paterno, apellido_materno

    def _extraer_datos_ocr(self, imagen_bytes):
        start_time = time.perf_counter()
        client = self._get_rekognition_client()
        response = client.detect_text(Image={'Bytes': imagen_bytes})
        detecciones = response.get('TextDetections', [])
        lineas = [d.get('DetectedText', '') for d in detecciones if d.get('Type') == 'LINE']
        texto_detectado = ' '.join(lineas)

        nombre, apellido_paterno, apellido_materno = self._extraer_nombre_apellidos(texto_detectado)
        curp_match = self._CURP_REGEX.search(texto_detectado)
        clave_match = self._CLAVE_ELECTOR_REGEX.search(texto_detectado)
        cic_match = self._CIC_REGEX.search(texto_detectado)
        cic_extraido = None
        if cic_match:
            cic_extraido = cic_match.group(1)
        else:
            cic_fallback_match = self._CIC_FALLBACK_REGEX.search(texto_detectado)
            if cic_fallback_match:
                cic_extraido = cic_fallback_match.group(0)
        ocr_id_cr_match = self._OCR_ID_CR_REGEX.search(texto_detectado)
        fecha_nac_match = self._FECHA_NAC_REGEX.search(texto_detectado)
        sexo_match = self._SEXO_REGEX.search(texto_detectado)
        vigencia_match = self._VIGENCIA_REGEX.search(texto_detectado)

        confidencias_lineas = [d.get('Confidence') for d in detecciones if d.get('Type') == 'LINE' and d.get('Confidence') is not None]
        promedio_confianza = round(sum(confidencias_lineas) / len(confidencias_lineas), 2) if confidencias_lineas else None
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        fecha_nacimiento = None
        if fecha_nac_match:
            fecha_nacimiento = timezone.datetime.strptime(fecha_nac_match.group(1).replace('-', '/'), '%d/%m/%Y').date()

        return {
            'nombre_extraido': nombre,
            'apellido_paterno_extraido': apellido_paterno,
            'apellido_materno_extraido': apellido_materno,
            'curp_extraida': curp_match.group(0) if curp_match else None,
            'clave_electoral_extraida': clave_match.group(0) if clave_match else None,
            'cic_extraido': cic_extraido,
            'ocr_id_cr_extraido': ocr_id_cr_match.group(0) if ocr_id_cr_match else None,
            'fecha_nacimiento_extraida': fecha_nacimiento,
            'sexo_extraido': sexo_match.group(1) if sexo_match else None,
            'vigencia_extraida': f"{vigencia_match.group(1)}-{vigencia_match.group(2)}" if vigencia_match else None,
            'confianza_ocr': promedio_confianza,
            'respuesta_ocr_completa': {'texto_detectado': texto_detectado},
            'texto_detectado': texto_detectado,
            'detecciones': len(detecciones),
            'tiempo_procesamiento_ms': elapsed_ms,
        }

    def _validar_campos_importantes(self, tipo_documento, datos_ocr):
        faltantes = []
        if tipo_documento == 'INE_FRONTAL':
            if not datos_ocr.get('curp_extraida'):
                faltantes.append('curp_extraida')
            if not datos_ocr.get('clave_electoral_extraida'):
                faltantes.append('clave_electoral_extraida')
        elif tipo_documento == 'INE_TRASERA':
            if not datos_ocr.get('cic_extraido'):
                faltantes.append('cic_extraido')
            if not datos_ocr.get('ocr_id_cr_extraido'):
                faltantes.append('ocr_id_cr_extraido')
        return faltantes

    def _buscar_duplicados(self, datos_ocr):
        duplicados = []
        validaciones = [
            ('curp_extraida', 'CURP'),
            ('cic_extraido', 'CIC'),
            ('ocr_id_cr_extraido', 'OCR_ID_CR'),
            ('clave_electoral_extraida', 'CLAVE_ELECTORAL'),
        ]
        for field_name, label in validaciones:
            valor = datos_ocr.get(field_name)
            if valor and DocumentosOCR.objects.filter(**{field_name: valor}).exists():
                duplicados.append({'campo': label, 'valor': valor})
        return duplicados

    def _crear_log(self, documento, estado_anterior, estado_nuevo, mensaje=None, error_detalle=None, tiempo_ms=None):
        LogOCR.objects.create(
            id_documento_ocr=documento,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            mensaje=mensaje,
            error_detalle=error_detalle,
            tiempo_procesamiento_ms=tiempo_ms
        )

    @extend_schema(
        tags=['OCR'],
        summary='Subir y procesar documento OCR',
        description='Recibe INE frontal/trasera, procesa OCR, valida campos clave y duplicados antes de guardar en base de datos.',
        request=DocumentoOCRUploadSerializer,
        responses={
            201: DocumentoOCRProcessResponseSerializer,
            400: OpenApiResponse(description='Datos inválidos o imagen faltante.'),
            409: OpenApiResponse(description='Conflicto por CURP/CIC/OCR_ID_CR/CLAVE_ELECTORAL duplicados.'),
            422: OpenApiResponse(description='No se reconocieron correctamente campos importantes del INE.'),
            500: OpenApiResponse(description='Error al procesar OCR.'),
        }
    )
    @action(detail=False, methods=['post'], url_path='subir-y-procesar', parser_classes=[MultiPartParser, FormParser])
    def subir_y_procesar(self, request):
        serializer = DocumentoOCRUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        archivo_frontal = data.get('archivo_frontal')
        archivo_trasera = data.get('archivo_trasera')
        id_relacionado = data.get('id_relacionado')

        estado_completado = self._get_estado_por_nombre('Completado')

        archivos_a_procesar = []
        if archivo_frontal:
            archivos_a_procesar.append(('INE_FRONTAL', archivo_frontal))
        if archivo_trasera:
            archivos_a_procesar.append(('INE_TRASERA', archivo_trasera))

        analisis = []
        errores_campos = []
        duplicados = []

        for tipo_doc_actual, archivo_actual in archivos_a_procesar:
            archivo_actual.seek(0)
            imagen_bytes = archivo_actual.read()
            try:
                datos_ocr = self._extraer_datos_ocr(imagen_bytes)
            except Exception as exc:
                return Response(
                    {
                        'detail': 'Error al procesar OCR.',
                        'tipo_documento': tipo_doc_actual,
                        'error': str(exc),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            faltantes = self._validar_campos_importantes(tipo_doc_actual, datos_ocr)
            if faltantes:
                errores_campos.append({
                    'tipo_documento': tipo_doc_actual,
                    'campos_faltantes': faltantes,
                    'texto_detectado': datos_ocr.get('texto_detectado', ''),
                })

            duplicados_en_doc = self._buscar_duplicados(datos_ocr)
            for item in duplicados_en_doc:
                duplicados.append({
                    'tipo_documento': tipo_doc_actual,
                    'campo': item['campo'],
                    'valor': item['valor'],
                })

            analisis.append({
                'tipo_documento': tipo_doc_actual,
                'archivo': archivo_actual,
                'datos_ocr': datos_ocr,
            })

        if errores_campos:
            return Response(
                {
                    'detail': 'No se reconocieron campos importantes del INE. No se guardó información.',
                    'errores_campos': errores_campos,
                },
                status=422
            )

        if duplicados:
            return Response(
                {
                    'detail': 'Se detectaron datos ya registrados (CURP/CIC/OCR_ID_CR/CLAVE_ELECTORAL). No se guardó información.',
                    'duplicados': duplicados,
                },
                status=status.HTTP_409_CONFLICT
            )

        resultados = []
        doc_frontal_id = None
        doc_trasera_id = None
        with transaction.atomic():
            for item in analisis:
                tipo_doc_actual = item['tipo_documento']
                archivo_actual = item['archivo']
                datos_ocr = item['datos_ocr']

                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = default_storage.save(f'ocr/{timestamp}_{archivo_actual.name}', archivo_actual)

                documento = DocumentosOCR.objects.create(
                    id_usuario=request.user,
                    tipo_documento=tipo_doc_actual,
                    id_relacionado=id_relacionado,
                    ruta_imagen=nombre_archivo,
                    id_estado=estado_completado,
                    fecha_procesamiento=timezone.now(),
                    intentos_procesamiento=1,
                    nombre_extraido=datos_ocr.get('nombre_extraido'),
                    apellido_paterno_extraido=datos_ocr.get('apellido_paterno_extraido'),
                    apellido_materno_extraido=datos_ocr.get('apellido_materno_extraido'),
                    curp_extraida=datos_ocr.get('curp_extraida'),
                    clave_electoral_extraida=datos_ocr.get('clave_electoral_extraida'),
                    cic_extraido=datos_ocr.get('cic_extraido'),
                    ocr_id_cr_extraido=datos_ocr.get('ocr_id_cr_extraido'),
                    fecha_nacimiento_extraida=datos_ocr.get('fecha_nacimiento_extraida'),
                    sexo_extraido=datos_ocr.get('sexo_extraido'),
                    vigencia_extraida=datos_ocr.get('vigencia_extraida'),
                    confianza_ocr=datos_ocr.get('confianza_ocr'),
                    respuesta_ocr_completa=datos_ocr.get('respuesta_ocr_completa'),
                )

                self._crear_log(
                    documento=documento,
                    estado_anterior=None,
                    estado_nuevo=estado_completado,
                    mensaje='Documento validado y guardado correctamente.',
                    tiempo_ms=datos_ocr.get('tiempo_procesamiento_ms')
                )

                resultados.append({'ok': True, 'documento': documento})

                if tipo_doc_actual == 'INE_FRONTAL':
                    doc_frontal_id = documento.id
                elif tipo_doc_actual == 'INE_TRASERA':
                    doc_trasera_id = documento.id

        campos_usuario = []
        if doc_frontal_id is not None:
            request.user.imagen_ine_frontal_url = str(doc_frontal_id)
            campos_usuario.append('imagen_ine_frontal_url')
        if doc_trasera_id is not None:
            request.user.imagen_ine_trasera_url = str(doc_trasera_id)
            campos_usuario.append('imagen_ine_trasera_url')
        if campos_usuario:
            request.user.save(update_fields=campos_usuario)

        status_code = status.HTTP_201_CREATED if all(r['ok'] for r in resultados) else status.HTTP_207_MULTI_STATUS
        response_payload = {
            'detail': 'Documentos OCR procesados y guardados correctamente.',
            'documentos': DocumentoOCRSerializer([r['documento'] for r in resultados], many=True).data,
            'resumen': {
                'total': len(resultados),
                'exitosos': len([r for r in resultados if r['ok']]),
                'fallidos': len([r for r in resultados if not r['ok']]),
                'errores': [
                    {'documento_id': r['documento'].id, 'error': r['error']}
                    for r in resultados if not r['ok']
                ]
            }
        }
        return Response(response_payload, status=status_code)


@extend_schema_view(
    list=extend_schema(tags=['Catálogos'], description='Listar estados OCR'),
    retrieve=extend_schema(tags=['Catálogos'], description='Obtener estado OCR'),
)
class EstadoOCRViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de estados OCR"""
    queryset = EstadoOCR.objects.all()
    serializer_class = EstadoOCRSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['OCR'], description='Listar logs OCR'),
    retrieve=extend_schema(tags=['OCR'], description='Obtener log OCR'),
)
class LogOCRViewSet(viewsets.ReadOnlyModelViewSet):
    """Historial de procesamiento OCR"""
    queryset = LogOCR.objects.all()
    serializer_class = LogOCRSerializer
    permission_classes = [IsAdminUser]