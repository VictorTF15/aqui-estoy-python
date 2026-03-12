from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

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
    DocumentoOCRSerializer, EstadoOCRSerializer, LogOCRSerializer
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
    list=extend_schema(tags=['Catálogos'], summary='Listar tipos de usuario', description='Obtiene los tipos de usuario disponibles.'),
    retrieve=extend_schema(tags=['Catálogos'], summary='Obtener tipo de usuario', description='Obtiene el detalle de un tipo de usuario por ID.'),
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
    list=extend_schema(tags=['Catálogos'], summary='Listar estados de caso', description='Obtiene los estados posibles para los casos.'),
    retrieve=extend_schema(tags=['Catálogos'], summary='Obtener estado de caso', description='Obtiene el detalle de un estado de caso por ID.'),
)
class EstadoCasoViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de estados de caso"""
    queryset = EstadoCaso.objects.all()
    serializer_class = EstadoCasoSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['Categorías'], summary='Listar categorías', description='Obtiene la lista de categorías.'),
    create=extend_schema(tags=['Categorías'], summary='Crear categoría', description='Crea una nueva categoría.'),
    retrieve=extend_schema(tags=['Categorías'], summary='Obtener categoría', description='Obtiene el detalle de una categoría por ID.'),
    update=extend_schema(tags=['Categorías'], summary='Actualizar categoría', description='Actualiza todos los campos de una categoría.'),
    partial_update=extend_schema(tags=['Categorías'], summary='Actualizar parcialmente categoría', description='Actualiza algunos campos de una categoría.'),
    destroy=extend_schema(tags=['Categorías'], summary='Eliminar categoría', description='Elimina una categoría.'),
)
class CategoriaViewSet(viewsets.ModelViewSet):
    """Gestión de categorías de casos"""
    queryset = Categorias.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Casos'], summary='Listar relaciones caso-categoría', description='Obtiene relaciones entre casos y categorías.'),
    create=extend_schema(tags=['Casos'], summary='Asignar categoría a caso', description='Crea una relación caso-categoría.'),
    retrieve=extend_schema(tags=['Casos'], summary='Obtener relación caso-categoría', description='Obtiene una relación por ID.'),
    update=extend_schema(tags=['Casos'], summary='Actualizar relación caso-categoría', description='Actualiza una relación completa.'),
    partial_update=extend_schema(tags=['Casos'], summary='Actualizar parcialmente relación', description='Actualiza algunos campos de una relación.'),
    destroy=extend_schema(tags=['Casos'], summary='Eliminar relación caso-categoría', description='Elimina una relación caso-categoría.'),
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
    list=extend_schema(tags=['Donaciones'], summary='Listar donaciones', description='Obtiene la lista de donaciones.'),
    create=extend_schema(tags=['Donaciones'], summary='Crear donación', description='Registra una nueva donación.'),
    retrieve=extend_schema(tags=['Donaciones'], summary='Obtener donación', description='Obtiene el detalle de una donación por ID.'),
    update=extend_schema(tags=['Donaciones'], summary='Actualizar donación', description='Actualiza una donación completa.'),
    partial_update=extend_schema(tags=['Donaciones'], summary='Actualizar parcialmente donación', description='Actualiza algunos campos de una donación.'),
    destroy=extend_schema(tags=['Donaciones'], summary='Eliminar donación', description='Elimina una donación.'),
)
class DonacionViewSet(viewsets.ModelViewSet):
    """Gestión de donaciones"""
    queryset = Donaciones.objects.all()
    serializer_class = DonacionSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-fecha_compromiso']

    @extend_schema(
        tags=['Donaciones'],
        summary='Mis donaciones',
        description='Obtiene las donaciones del usuario autenticado.'
    )
    @action(detail=False, methods=['get'])
    def mis_donaciones(self, request):
        donaciones = self.get_queryset().filter(id_donador=request.user)
        serializer = self.get_serializer(donaciones, many=True)
        return Response(serializer.data)


# ============================================
# EVIDENCIAS
# ============================================

@extend_schema_view(
    list=extend_schema(tags=['Evidencias'], summary='Listar evidencias', description='Obtiene evidencias multimedia asociadas a casos.'),
    create=extend_schema(tags=['Evidencias'], summary='Crear evidencia', description='Sube o registra una nueva evidencia.'),
    retrieve=extend_schema(tags=['Evidencias'], summary='Obtener evidencia', description='Obtiene el detalle de una evidencia por ID.'),
    update=extend_schema(tags=['Evidencias'], summary='Actualizar evidencia', description='Actualiza una evidencia completa.'),
    partial_update=extend_schema(tags=['Evidencias'], summary='Actualizar parcialmente evidencia', description='Actualiza algunos campos de una evidencia.'),
    destroy=extend_schema(tags=['Evidencias'], summary='Eliminar evidencia', description='Elimina una evidencia.'),
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
    list=extend_schema(tags=['Mensajería'], summary='Listar conversaciones', description='Obtiene conversaciones del sistema.'),
    create=extend_schema(tags=['Mensajería'], summary='Crear conversación', description='Crea una nueva conversación.'),
    retrieve=extend_schema(tags=['Mensajería'], summary='Obtener conversación', description='Obtiene el detalle de una conversación por ID.'),
    update=extend_schema(tags=['Mensajería'], summary='Actualizar conversación', description='Actualiza una conversación completa.'),
    partial_update=extend_schema(tags=['Mensajería'], summary='Actualizar parcialmente conversación', description='Actualiza algunos campos de una conversación.'),
    destroy=extend_schema(tags=['Mensajería'], summary='Eliminar conversación', description='Elimina una conversación.'),
)
class ConversacionViewSet(viewsets.ModelViewSet):
    """Gestión de conversaciones"""
    queryset = Conversaciones.objects.all()
    serializer_class = ConversacionSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Mensajería'], summary='Listar mensajes', description='Obtiene los mensajes disponibles.'),
    create=extend_schema(tags=['Mensajería'], summary='Enviar mensaje', description='Crea un nuevo mensaje.'),
    retrieve=extend_schema(tags=['Mensajería'], summary='Obtener mensaje', description='Obtiene el detalle de un mensaje por ID.'),
    update=extend_schema(tags=['Mensajería'], summary='Actualizar mensaje', description='Actualiza un mensaje completo.'),
    partial_update=extend_schema(tags=['Mensajería'], summary='Actualizar parcialmente mensaje', description='Actualiza algunos campos de un mensaje.'),
    destroy=extend_schema(tags=['Mensajería'], summary='Eliminar mensaje', description='Elimina un mensaje.'),
)
class MensajeViewSet(viewsets.ModelViewSet):
    """Gestión de mensajes"""
    queryset = Mensajes.objects.all()
    serializer_class = MensajeSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-fecha_envio']


@extend_schema_view(
    list=extend_schema(tags=['Catálogos'], summary='Listar tipos de mensaje', description='Obtiene tipos de mensaje disponibles.'),
    retrieve=extend_schema(tags=['Catálogos'], summary='Obtener tipo de mensaje', description='Obtiene el detalle de un tipo de mensaje por ID.'),
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
    list=extend_schema(tags=['Moderación'], summary='Listar reportes', description='Obtiene reportes de moderación.'),
    create=extend_schema(tags=['Moderación'], summary='Crear reporte', description='Registra un nuevo reporte.'),
    retrieve=extend_schema(tags=['Moderación'], summary='Obtener reporte', description='Obtiene el detalle de un reporte por ID.'),
    update=extend_schema(tags=['Moderación'], summary='Actualizar reporte', description='Actualiza un reporte completo.'),
    partial_update=extend_schema(tags=['Moderación'], summary='Actualizar parcialmente reporte', description='Actualiza algunos campos de un reporte.'),
    destroy=extend_schema(tags=['Moderación'], summary='Eliminar reporte', description='Elimina un reporte.'),
)
class ReporteViewSet(viewsets.ModelViewSet):
    """Gestión de reportes"""
    queryset = Reportes.objects.all()
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Catálogos'], summary='Listar estados de reporte', description='Obtiene estados posibles de reporte.'),
    retrieve=extend_schema(tags=['Catálogos'], summary='Obtener estado de reporte', description='Obtiene el detalle de un estado de reporte por ID.'),
)
class EstadoReporteViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de estados de reporte"""
    queryset = EstadoReporte.objects.all()
    serializer_class = EstadoReporteSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['Moderación'], summary='Listar sanciones', description='Obtiene sanciones registradas.'),
    create=extend_schema(tags=['Moderación'], summary='Crear sanción', description='Registra una nueva sanción.'),
    retrieve=extend_schema(tags=['Moderación'], summary='Obtener sanción', description='Obtiene el detalle de una sanción por ID.'),
    update=extend_schema(tags=['Moderación'], summary='Actualizar sanción', description='Actualiza una sanción completa.'),
    partial_update=extend_schema(tags=['Moderación'], summary='Actualizar parcialmente sanción', description='Actualiza algunos campos de una sanción.'),
    destroy=extend_schema(tags=['Moderación'], summary='Eliminar sanción', description='Elimina una sanción.'),
)
class SancionViewSet(viewsets.ModelViewSet):
    """Gestión de sanciones"""
    queryset = Sanciones.objects.all()
    serializer_class = SancionSerializer
    permission_classes = [IsAdminUser]


@extend_schema_view(
    list=extend_schema(tags=['Catálogos'], summary='Listar tipos de sanción', description='Obtiene tipos de sanción disponibles.'),
    retrieve=extend_schema(tags=['Catálogos'], summary='Obtener tipo de sanción', description='Obtiene el detalle de un tipo de sanción por ID.'),
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
    list=extend_schema(tags=['OCR'], summary='Listar documentos OCR', description='Obtiene documentos enviados para OCR.'),
    create=extend_schema(tags=['OCR'], summary='Crear documento OCR', description='Registra/sube un documento para procesamiento OCR.'),
    retrieve=extend_schema(tags=['OCR'], summary='Obtener documento OCR', description='Obtiene el detalle de un documento OCR por ID.'),
    update=extend_schema(tags=['OCR'], summary='Actualizar documento OCR', description='Actualiza un documento OCR completo.'),
    partial_update=extend_schema(tags=['OCR'], summary='Actualizar parcialmente documento OCR', description='Actualiza algunos campos de un documento OCR.'),
    destroy=extend_schema(tags=['OCR'], summary='Eliminar documento OCR', description='Elimina un documento OCR.'),
)
class DocumentoOCRViewSet(viewsets.ModelViewSet):
    """Gestión de documentos OCR"""
    queryset = DocumentosOCR.objects.all()
    serializer_class = DocumentoOCRSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Catálogos'], summary='Listar estados OCR', description='Obtiene estados posibles del flujo OCR.'),
    retrieve=extend_schema(tags=['Catálogos'], summary='Obtener estado OCR', description='Obtiene el detalle de un estado OCR por ID.'),
)
class EstadoOCRViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de estados OCR"""
    queryset = EstadoOCR.objects.all()
    serializer_class = EstadoOCRSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['OCR'], summary='Listar logs OCR', description='Obtiene el historial de procesamiento OCR.'),
    retrieve=extend_schema(tags=['OCR'], summary='Obtener log OCR', description='Obtiene el detalle de un registro de log OCR por ID.'),
)
class LogOCRViewSet(viewsets.ReadOnlyModelViewSet):
    """Historial de procesamiento OCR"""
    queryset = LogOCR.objects.all()
    serializer_class = LogOCRSerializer
    permission_classes = [IsAdminUser]