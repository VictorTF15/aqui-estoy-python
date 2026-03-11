from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.exceptions import ValidationError
from django.db.models import Q, Count
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema, extend_schema_view

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
    EstadoCasoSerializer, CategoriaSerializer,
    CasoCategoriaSerializer, DonacionSerializer,
    EvidenciaSerializer, ConversacionSerializer, MensajeSerializer,
    TipoMensajeSerializer, ReporteSerializer, EstadoReporteSerializer,
    SancionSerializer, TipoSancionSerializer, DocumentoOCRSerializer,
    EstadoOCRSerializer, LogOCRSerializer
)


# ============================================
# AUTENTICACIÓN
# ============================================

@extend_schema(
    tags=['Autenticación'],
    description='Login con correo electrónico y contraseña',
    request=CustomTokenObtainPairSerializer,
    responses={200: CustomTokenObtainPairSerializer}
)
class CustomTokenObtainPairView(APIView):
    """Login con correo electrónico y contraseña"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        print("=== DEBUG LOGIN ===")
        print(f"Request data: {request.data}")
        print(f"Request content type: {request.content_type}")
        
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        
        try:
            print(f"Serializer initial data: {serializer.initial_data}")
            is_valid = serializer.is_valid(raise_exception=False)
            print(f"Is valid: {is_valid}")
            
            if not is_valid:
                print(f"Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"Validated data: {serializer.validated_data}")
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            print(f"ValidationError: {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Exception: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'detail': 'Error al procesar la solicitud'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================
# USUARIOS
# ============================================

@extend_schema_view(
    list=extend_schema(tags=['Usuarios'], description='Listar todos los usuarios'),
    create=extend_schema(tags=['Usuarios'], description='Crear un nuevo usuario'),
    retrieve=extend_schema(tags=['Usuarios'], description='Obtener detalles de un usuario'),
    update=extend_schema(tags=['Usuarios'], description='Actualizar un usuario'),
    partial_update=extend_schema(tags=['Usuarios'], description='Actualizar parcialmente un usuario'),
    destroy=extend_schema(tags=['Usuarios'], description='Eliminar un usuario'),
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

    @extend_schema(tags=['Usuarios'], description='Obtener datos del usuario autenticado')
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(tags=['Usuarios'], description='Cambiar contraseña de usuario')
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
    list=extend_schema(tags=['Casos'], description='Listar todos los casos'),
    create=extend_schema(tags=['Casos'], description='Crear un nuevo caso'),
    retrieve=extend_schema(tags=['Casos'], description='Obtener detalles de un caso'),
    update=extend_schema(tags=['Casos'], description='Actualizar un caso'),
    partial_update=extend_schema(tags=['Casos'], description='Actualizar parcialmente un caso'),
    destroy=extend_schema(tags=['Casos'], description='Eliminar un caso'),
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

    @extend_schema(tags=['Casos'], description='Obtener casos para visualizar en mapa')
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

    @extend_schema(tags=['Casos'], description='Obtener estadísticas de casos')
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