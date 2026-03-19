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
from .services import UsuarioService, DocumentoOCRService
from .selectors import CasoSelector, DonacionSelector

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
    # permission_classes = [IsAuthenticated] # Se manejará dinámicamente
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombres', 'apellido_paterno', 'apellido_materno', 'correo']
    ordering = ['-fecha_registro']

    def get_permissions(self):
        """
        Asigna permisos basados en la acción.
        - `create` (registro) es público.
        - Otras acciones requieren autenticación.
        """
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

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
        try:
            UsuarioService.cambiar_password(
                usuario=usuario,
                password_actual=request.data.get('password_actual'),
                password_nueva=request.data.get('password_nueva')
            )
            return Response({'message': 'Contraseña actualizada'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
        return Response(CasoSelector.get_casos_mapa())

    @extend_schema(
        tags=['Casos'],
        summary='Estadísticas de casos',
        description='Devuelve totales de casos (total, abiertos y cerrados).'
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        return Response(CasoSelector.get_estadisticas())


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
        donaciones = DonacionSelector.get_donaciones_por_usuario(request.user.id)
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
        archivos_a_procesar = []
        if data.get('archivo_frontal'):
            archivos_a_procesar.append(('INE_FRONTAL', data.get('archivo_frontal')))
        if data.get('archivo_trasera'):
            archivos_a_procesar.append(('INE_TRASERA', data.get('archivo_trasera')))

        try:
            resultado = DocumentoOCRService.procesar_archivos(
                usuario=request.user,
                archivos_a_procesar=archivos_a_procesar,
                id_relacionado=data.get('id_relacionado')
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not resultado.get('ok'):
            if resultado.get('errores_campos'):
                return Response(
                    {'detail': 'No se reconocieron campos importantes del INE. No se guardó información.', 'errores_campos': resultado['errores_campos']},
                    status=422
                )
            if resultado.get('duplicados'):
                return Response(
                    {'detail': 'Se detectaron datos ya registrados.', 'duplicados': resultado['duplicados']},
                    status=status.HTTP_409_CONFLICT
                )

        resultados = resultado['resultados']
        status_code = status.HTTP_201_CREATED if len(resultados) == len(archivos_a_procesar) else status.HTTP_207_MULTI_STATUS
        return Response({
            'detail': 'Documentos procesados.',
            'documentos': DocumentoOCRSerializer(resultados, many=True).data,
            'resumen': {'total': len(resultados), 'exitosos': len(resultados), 'fallidos': 0, 'errores': []}
        }, status=status_code)


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