from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Usuarios, Casos, Donaciones, Categorias, EstadoCaso, CasoCategorias  # ✅ Cambiado
from .serializers import (
    UsuarioSerializer, CasoListSerializer, CasoDetailSerializer,
    CasoCreateUpdateSerializer, DonacionSerializer, DonacionCreateSerializer,
    CategoriaSerializer, EstadoCasoSerializer
)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios.
    
    list: Listar todos los usuarios (solo admin)
    retrieve: Obtener detalle de un usuario
    create: Crear nuevo usuario (solo admin)
    update: Actualizar usuario (solo admin)
    destroy: Eliminar usuario (solo admin)
    me: Obtener perfil del usuario autenticado
    """
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['esta_activo', 'id_tipo_usuario']
    search_fields = ['nombres', 'apellido_paterno', 'correo']
    ordering_fields = ['fecha_registro', 'nombres']
    ordering = ['-fecha_registro']
    
    def get_queryset(self):
        return Usuarios.objects.select_related('id_tipo_usuario').all()
    
    def get_permissions(self):
        """Solo admin puede listar/editar/eliminar usuarios"""
        if self.action in ['list', 'destroy', 'update', 'partial_update', 'create']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="Obtener perfil del usuario autenticado",
        responses={200: UsuarioSerializer}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Obtener perfil del usuario actual"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'No autenticado'}, status=401)
        
        try:
            usuario = Usuarios.objects.get(pk=user_id)
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)


class CasoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar casos.
    
    list: Listar todos los casos públicos
    retrieve: Obtener detalle de un caso
    create: Crear nuevo caso (requiere autenticación)
    mapa: Obtener casos con coordenadas para mapa
    compartir: Incrementar contador de veces compartido
    """
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id_estado', 'esta_abierto', 'entidad', 'colonia']
    search_fields = ['titulo', 'descripcion', 'colonia']
    ordering_fields = ['fecha_creacion', 'vistas', 'compartido']
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        queryset = Casos.objects.select_related(
            'id_beneficiario', 
            'id_estado'
        ).filter(esta_abierto=True)
        
        # Filtro por categoría
        categoria = self.request.query_params.get('categoria', None)
        if categoria:
            casos_ids = CasoCategorias.objects.filter(  # ✅ Cambiado
                id_categoria_id=categoria
            ).values_list('id_caso_id', flat=True)
            queryset = queryset.filter(id__in=casos_ids)
        
        return queryset.distinct()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CasoListSerializer
        elif self.action == 'retrieve':
            return CasoDetailSerializer
        return CasoCreateUpdateSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Incrementar vistas al ver detalle"""
        instance = self.get_object()
        instance.vistas += 1
        instance.save(update_fields=['vistas'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Obtener casos con coordenadas para mapa",
        manual_parameters=[
            openapi.Parameter('categoria', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('estado', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    @action(detail=False, methods=['get'])
    def mapa(self, request):
        """Casos con coordenadas para mapa"""
        casos = self.get_queryset().filter(
            latitud__isnull=False,
            longitud__isnull=False
        ).exclude(
            Q(latitud=0) | Q(longitud=0)
        )
        
        serializer = CasoDetailSerializer(casos, many=True)
        return Response({
            'success': True,
            'casos': serializer.data,
            'total': len(serializer.data)
        })
    
    @action(detail=True, methods=['post'])
    def compartir(self, request, pk=None):
        """Incrementar contador de compartidos"""
        caso = self.get_object()
        caso.compartido += 1
        caso.save(update_fields=['compartido'])
        return Response({
            'success': True,
            'compartido': caso.compartido
        })


class DonacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar donaciones.
    """
    serializer_class = DonacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado_donacion', 'id_caso']
    ordering_fields = ['fecha_compromiso', 'monto']
    ordering = ['-fecha_compromiso']
    
    def get_queryset(self):
        return Donaciones.objects.select_related('id_donador', 'id_caso').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DonacionCreateSerializer
        return DonacionSerializer
    
    @action(detail=False, methods=['get'])
    def mis_donaciones(self, request):
        """Donaciones del usuario autenticado"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'No autenticado'}, status=401)
        
        donaciones = self.get_queryset().filter(id_donador_id=user_id)
        serializer = self.get_serializer(donaciones, many=True)
        return Response(serializer.data)


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para categorías.
    """
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Categorias.objects.filter(es_activo=True).annotate(
            total_casos=Count('casocategorias')
        ).order_by('nombre')
    
    @action(detail=True, methods=['get'])
    def casos(self, request, pk=None):
        """Casos de una categoría"""
        categoria = self.get_object()
        casos_ids = CasoCategorias.objects.filter(  # ✅ Cambiado
            id_categoria=categoria
        ).values_list('id_caso_id', flat=True)
        
        casos = Casos.objects.filter(id__in=casos_ids)
        serializer = CasoListSerializer(casos, many=True)
        return Response(serializer.data)


class EstadoCasoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para estados de casos.
    """
    serializer_class = EstadoCasoSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return EstadoCaso.objects.all().order_by('nombre')  # ✅ Cambiado