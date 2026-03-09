from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth.hashers import check_password, make_password
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import (
    Usuarios, TipoUsuario, Casos, EstadoCaso, Categorias, CasoCategorias,
    Donaciones, Evidencias, Conversaciones, Mensajes, TipoMensaje,
    Reportes, EstadoReporte, Sanciones, TipoSancion, DocumentosOCR,
    EstadoOCR, LogOCR
)
from .serializers import (
    UsuarioListSerializer, UsuarioDetailSerializer, UsuarioCreateSerializer,
    UsuarioUpdateSerializer, CambiarContrasenaSerializer, ActualizarTelefonoSerializer,
    AsignarTipoUsuarioSerializer, TipoUsuarioSerializer, CasoListSerializer, CasoDetailSerializer,
    CasoCreateUpdateSerializer, EstadoCasoSerializer, CategoriaSerializer,
    CasoCategoriaSerializer, DonacionSerializer, DonacionCreateSerializer,
    EvidenciaSerializer, ConversacionSerializer, MensajeSerializer,
    TipoMensajeSerializer, ReporteSerializer, EstadoReporteSerializer,
    SancionSerializer, TipoSancionSerializer, DocumentoOCRSerializer,
    EstadoOCRSerializer, LogOCRSerializer
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para autenticación con correo"""
    
    # Sobrescribir los campos por defecto
    username_field = 'correo'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Reemplazar el campo username por correo
        self.fields['correo'] = serializers.EmailField(required=True)
        self.fields['contrasena'] = serializers.CharField(write_only=True, required=True)
        
        # Eliminar campos que no usamos
        self.fields.pop('username', None)
        self.fields.pop('password', None)
    
    def validate(self, attrs):
        """Validar credenciales personalizadas"""
        correo = attrs.get('correo')
        contrasena = attrs.get('contrasena')
        
        if not correo or not contrasena:
            raise serializers.ValidationError({
                'detail': 'Debe proporcionar correo y contraseña'
            })
        
        # Autenticar con el backend de Django
        # Django espera 'username' y 'password', así que los mapeamos
        user = authenticate(
            request=self.context.get('request'),
            username=correo,  # Django busca por USERNAME_FIELD (que es 'correo')
            password=contrasena
        )
        
        if not user:
            raise serializers.ValidationError({
                'detail': 'Credenciales incorrectas'
            })
        
        if not user.is_active:
            raise serializers.ValidationError({
                'detail': 'Usuario inactivo o deshabilitado'
            })
        
        # Generar tokens JWT
        refresh = self.get_token(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'correo': user.correo,
                'nombres': user.nombres,
                'apellido_paterno': user.apellido_paterno,
            }
        }

class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para obtener tokens JWT"""
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Usuarios'],
        summary='[WEB ADMIN] Obtener usuarios activos',
        description='Roles: Administrador. Retorna la lista completa de usuarios activos en el sistema.',
        responses={
            200: OpenApiExample(
                'Respuesta exitosa',
                value={
                    "mensaje": "Usuarios obtenidos correctamente",
                    "data": [
                        {
                            "id": 1,
                            "nombres": "Juan",
                            "apellido_paterno": "Pérez",
                            "apellido_materno": "García",
                            "correo": "juan.perez@example.com",
                            "telefono": "5512345678",
                            "tipo_usuario": "Beneficiario",
                            "ciudad": "CDMX",
                            "estado": "Ciudad de México",
                            "esta_activo": True,
                            "verificado": True,
                            "fecha_registro": "2026-01-15T10:30:00Z"
                        }
                    ]
                }
            ),
            401: OpenApiExample('No autorizado', value={'error': 'Token JWT requerido'}),
            403: OpenApiExample('Permiso denegado', value={'error': 'Rol insuficiente'}),
        }
    ),
    create=extend_schema(
        tags=['Usuarios'],
        summary='[WEB ADMIN] Crear usuario',
        description='Roles: Administrador. Registra un nuevo usuario en el sistema con sus datos personales, tipo de usuario y contraseña encriptada.',
        request=UsuarioCreateSerializer,
        examples=[
            OpenApiExample(
                'Ejemplo de creación de usuario',
                value={
                    "nombres": "Juan",
                    "apellido_paterno": "Pérez",
                    "apellido_materno": "García",
                    "correo": "juan.perez@example.com",
                    "telefono": "5512345678",
                    "id_tipo_usuario": 1,
                    "ciudad": "CDMX",
                    "estado": "Ciudad de México",
                    "colonia": "Del Valle",
                    "direccion": "Av. Insurgentes Sur 123",
                    "codigo_postal": "03100",
                    "contrasena": "Password123!"
                }
            )
        ],
        responses={
            201: OpenApiExample(
                'Usuario creado',
                value={
                    "mensaje": "Usuario creado correctamente",
                    "data": {
                        "id": 1,
                        "nombres": "Juan",
                        "apellido_paterno": "Pérez",
                        "correo": "juan.perez@example.com",
                        "esta_activo": True
                    }
                }
            ),
            400: OpenApiExample('Error validación', value={'error': 'Datos inválidos'}),
            409: OpenApiExample('Usuario existe', value={'error': 'El correo ya está registrado'}),
        }
    ),
    retrieve=extend_schema(
        tags=['Usuarios'],
        summary='[WEB / WEB ADMIN] Obtener usuario por ID',
        description='Roles: Usuario autenticado o Administrador. Obtiene los detalles completos de un usuario específico por su ID.',
        responses={
            200: UsuarioDetailSerializer,
            404: OpenApiExample('No encontrado', value={'error': 'Usuario no encontrado'}),
        }
    ),
    update=extend_schema(
        tags=['Usuarios'],
        summary='[WEB ADMIN] Actualizar usuario completo',
        description='Roles: Administrador. Actualiza todos los campos permitidos de un usuario.',
        request=UsuarioUpdateSerializer,
        responses={200: UsuarioDetailSerializer}
    ),
    partial_update=extend_schema(
        tags=['Usuarios'],
        summary='[WEB ADMIN] Actualizar usuario parcial',
        description='Roles: Administrador. Actualiza solo los campos enviados de un usuario.',
        request=UsuarioUpdateSerializer,
        examples=[
            OpenApiExample(
                'Actualizar solo teléfono y ciudad',
                value={
                    "telefono": "5587654321",
                    "ciudad": "Guadalajara"
                }
            )
        ],
        responses={200: UsuarioDetailSerializer}
    ),
    destroy=extend_schema(
        tags=['Usuarios'],
        summary='[WEB ADMIN] Eliminar usuario (soft delete)',
        description='Roles: Administrador. Marca el usuario como inactivo sin eliminarlo permanentemente de la base de datos.',
        responses={
            200: OpenApiExample('Usuario eliminado', value={'mensaje': 'Usuario desactivado correctamente'}),
            404: OpenApiExample('No encontrado', value={'error': 'Usuario no encontrado'}),
        }
    ),
)
class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Usuarios.objects.select_related('id_tipo_usuario').all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UsuarioListSerializer
        elif self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        return UsuarioDetailSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'destroy', 'create']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'mensaje': 'Usuarios obtenidos correctamente', 'data': serializer.data})
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'mensaje': 'Usuario creado correctamente', 'data': UsuarioDetailSerializer(serializer.instance).data},
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'mensaje': 'Usuario obtenido correctamente', 'data': serializer.data})
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'mensaje': 'Usuario actualizado correctamente', 'data': serializer.data})
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.esta_activo = False
        instance.save()
        return Response({'mensaje': 'Usuario desactivado correctamente'}, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Usuarios'],
        summary='[WEB ADMIN] Obtener usuarios inactivos',
        description='Roles: Administrador. Retorna la lista de usuarios deshabilitados o inactivos en el sistema.',
        responses={200: UsuarioListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser], url_path='inactivos')
    def inactivos(self, request):
        usuarios = self.get_queryset().filter(esta_activo=False)
        serializer = UsuarioListSerializer(usuarios, many=True)
        return Response({'mensaje': 'Usuarios inactivos obtenidos correctamente', 'data': serializer.data})
    
    @extend_schema(
        tags=['Usuarios'],
        summary='[WEB / WEB ADMIN] Obtener mi perfil',
        description='Roles: Usuario autenticado. Retorna la información del usuario autenticado actualmente en sesión.',
        responses={
            200: UsuarioDetailSerializer,
            401: OpenApiExample('No autenticado', value={'error': 'Token JWT requerido'}),
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='me')
    def me(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'No autenticado'}, status=401)
        try:
            usuario = Usuarios.objects.get(pk=user_id)
            serializer = UsuarioDetailSerializer(usuario)
            return Response({'mensaje': 'Usuario obtenido correctamente', 'data': serializer.data})
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)
    
    @extend_schema(
        tags=['Usuarios'],
        summary='[WEB] Actualizar mi perfil',
        description='Roles: Usuario autenticado. Permite al usuario actualizar su información personal como nombres, teléfono, dirección, etc.',
        request=UsuarioUpdateSerializer,
        examples=[
            OpenApiExample(
                'Actualizar perfil',
                value={
                    "nombres": "Juan Carlos",
                    "telefono": "5512345678",
                    "ciudad": "Monterrey",
                    "direccion": "Calle Nueva 456"
                }
            )
        ],
        responses={200: UsuarioDetailSerializer}
    )
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], url_path='me/perfil')
    def actualizar_perfil(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'No autenticado'}, status=401)
        try:
            usuario = Usuarios.objects.get(pk=user_id)
            serializer = UsuarioUpdateSerializer(usuario, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'mensaje': 'Perfil actualizado correctamente', 'data': UsuarioDetailSerializer(usuario).data})
            return Response({'error': serializer.errors}, status=400)
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)
    
    @extend_schema(
        tags=['Usuarios'],
        summary='[WEB] Actualizar mi teléfono',
        description='Roles: Usuario autenticado. Permite al usuario cambiar su número de teléfono de contacto.',
        request=ActualizarTelefonoSerializer,
        examples=[
            OpenApiExample('Actualizar teléfono', value={"telefono": "5598765432"})
        ],
        responses={
            200: OpenApiExample('Éxito', value={'mensaje': 'Teléfono actualizado correctamente'}),
        }
    )
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], url_path='me/telefono')
    def actualizar_telefono(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'No autenticado'}, status=401)
        try:
            usuario = Usuarios.objects.get(pk=user_id)
            serializer = ActualizarTelefonoSerializer(data=request.data)
            if serializer.is_valid():
                usuario.telefono = serializer.validated_data['telefono']
                usuario.save()
                return Response({'mensaje': 'Teléfono actualizado correctamente'})
            return Response({'error': serializer.errors}, status=400)
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)
    
    @extend_schema(
        tags=['Usuarios'],
        summary='[WEB] Cambiar mi contraseña',
        description='Roles: Usuario autenticado. Permite al usuario cambiar su contraseña proporcionando la contraseña actual y la nueva contraseña.',
        request=CambiarContrasenaSerializer,
        examples=[
            OpenApiExample(
                'Cambiar contraseña',
                value={
                    "contrasena_actual": "Password123!",
                    "contrasena_nueva": "NewPassword456!",
                    "confirmar_contrasena": "NewPassword456!"
                }
            )
        ],
        responses={
            200: OpenApiExample('Éxito', value={'mensaje': 'Contraseña actualizada correctamente'}),
            400: OpenApiExample('Error', value={'error': 'Contraseña actual incorrecta'}),
        }
    )
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], url_path='me/contrasena')
    def cambiar_contrasena(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'No autenticado'}, status=401)
        try:
            usuario = Usuarios.objects.get(pk=user_id)
            serializer = CambiarContrasenaSerializer(data=request.data)
            if serializer.is_valid():
                if not check_password(serializer.validated_data['contrasena_actual'], usuario.contrasena):
                    return Response({'error': 'Contraseña actual incorrecta'}, status=400)
                usuario.contrasena = make_password(serializer.validated_data['contrasena_nueva'])
                usuario.save()
                return Response({'mensaje': 'Contraseña actualizada correctamente'})
            return Response({'error': serializer.errors}, status=400)
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)
    
    @extend_schema(
        tags=['Usuarios'],
        summary='[WEB ADMIN] Inhabilitar usuario',
        description='Roles: Administrador. Desactiva un usuario específico del sistema sin eliminarlo permanentemente.',
        responses={200: OpenApiExample('Éxito', value={'mensaje': 'Usuario inhabilitado correctamente'})}
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser], url_path='inhabilitar')
    def inhabilitar(self, request, pk=None):
        usuario = self.get_object()
        usuario.esta_activo = False
        usuario.save()
        return Response({'mensaje': 'Usuario inhabilitado correctamente'})
    
    @extend_schema(
        tags=['Usuarios'],
        summary='[WEB ADMIN] Habilitar usuario',
        description='Roles: Administrador. Reactiva un usuario previamente desactivado en el sistema.',
        responses={200: OpenApiExample('Éxito', value={'mensaje': 'Usuario habilitado correctamente'})}
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser], url_path='habilitar')
    def habilitar(self, request, pk=None):
        usuario = self.get_object()
        usuario.esta_activo = True
        usuario.save()
        return Response({'mensaje': 'Usuario habilitado correctamente'})
    
    @extend_schema(
        tags=['Usuarios'],
        summary='[WEB ADMIN] Asignar tipo de usuario',
        description='Roles: Administrador. Asigna o cambia el tipo/rol de un usuario específico (Beneficiario, Donador, Voluntario, etc).',
        request=AsignarTipoUsuarioSerializer,
        examples=[
            OpenApiExample('Asignar tipo', value={"id_tipo_usuario": 2})
        ],
        responses={200: OpenApiExample('Éxito', value={'mensaje': 'Tipo de usuario asignado correctamente'})}
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser], url_path='asignar-tipo')
    def asignar_tipo(self, request, pk=None):
        usuario = self.get_object()
        serializer = AsignarTipoUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            tipo_id = serializer.validated_data['id_tipo_usuario']
            try:
                tipo_usuario = TipoUsuario.objects.get(pk=tipo_id)
                usuario.id_tipo_usuario = tipo_usuario
                usuario.save()
                return Response({'mensaje': 'Tipo de usuario asignado correctamente'})
            except TipoUsuario.DoesNotExist:
                return Response({'error': 'Tipo de usuario no encontrado'}, status=404)
        return Response({'error': serializer.errors}, status=400)


@extend_schema_view(
    list=extend_schema(
        tags=['Tipos de Usuario'],
        summary='[WEB / WEB ADMIN] Listar tipos de usuario',
        description='Roles: Cualquier usuario. Retorna el catálogo completo de tipos de usuario disponibles (Beneficiario, Donador, Voluntario, etc).'
    ),
    create=extend_schema(
        tags=['Tipos de Usuario'],
        summary='[WEB ADMIN] Crear tipo de usuario',
        description='Roles: Administrador. Crea un nuevo tipo de usuario en el catálogo del sistema.',
        examples=[
            OpenApiExample(
                'Crear tipo',
                value={
                    "nombre": "Voluntario",
                    "descripcion": "Usuario que ofrece apoyo voluntario en casos sociales"
                }
            )
        ]
    ),
    retrieve=extend_schema(tags=['Tipos de Usuario'], summary='[WEB ADMIN] Obtener tipo por ID'),
    update=extend_schema(tags=['Tipos de Usuario'], summary='[WEB ADMIN] Actualizar tipo completo'),
    partial_update=extend_schema(tags=['Tipos de Usuario'], summary='[WEB ADMIN] Actualizar tipo parcial'),
    destroy=extend_schema(tags=['Tipos de Usuario'], summary='[WEB ADMIN] Eliminar tipo'),
)
class TipoUsuarioViewSet(viewsets.ModelViewSet):
    queryset = TipoUsuario.objects.all()
    serializer_class = TipoUsuarioSerializer
    permission_classes = [AllowAny]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'mensaje': 'Tipos de usuario obtenidos correctamente', 'data': serializer.data})


@extend_schema_view(
    list=extend_schema(
        tags=['Casos'],
        summary='[WEB / WEB ADMIN] Listar casos',
        description='Roles: Cualquier usuario. Retorna todos los casos abiertos y disponibles en el sistema para visualización o apoyo.'
    ),
    create=extend_schema(
        tags=['Casos'],
        summary='[WEB] Crear caso',
        description='Roles: Usuario autenticado (beneficiario). Registra un nuevo caso social en el sistema con descripción, ubicación y evidencias.',
        examples=[
            OpenApiExample(
                'Crear caso básico',
                value={
                    "titulo": "Familia necesita apoyo alimentario urgente",
                    "descripcion": "Familia de 5 personas en situación de vulnerabilidad económica requiere apoyo con despensa básica",
                    "entidad": "Ciudad de México",
                    "colonia": "Iztapalapa",
                    "direccion": "Calle Reforma 123",
                    "codigo_postal": "09800",
                    "id_beneficiario": 1,
                    "categorias": [1, 3],
                    "latitud": "19.3523",
                    "longitud": "-99.0993"
                }
            )
        ]
    ),
    retrieve=extend_schema(tags=['Casos'], summary='[WEB / WEB ADMIN] Obtener caso por ID', description='Roles: Cualquier usuario. Incrementa automáticamente el contador de vistas del caso.'),
    update=extend_schema(tags=['Casos'], summary='[WEB ADMIN] Actualizar caso completo'),
    partial_update=extend_schema(tags=['Casos'], summary='[WEB / WEB ADMIN] Actualizar caso parcial'),
    destroy=extend_schema(tags=['Casos'], summary='[WEB ADMIN] Eliminar caso'),
)
class CasoViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Casos.objects.select_related('id_beneficiario', 'id_estado').filter(esta_abierto=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CasoListSerializer
        elif self.action == 'retrieve':
            return CasoDetailSerializer
        return CasoCreateUpdateSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'mensaje': 'Casos obtenidos correctamente', 'data': serializer.data})
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.vistas += 1
        instance.save(update_fields=['vistas'])
        serializer = self.get_serializer(instance)
        return Response({'mensaje': 'Caso obtenido correctamente', 'data': serializer.data})
    
    @extend_schema(
        tags=['Casos'],
        summary='[WEB / WEB ADMIN] Obtener casos con coordenadas para mapa',
        description='Roles: Cualquier usuario. Retorna todos los casos que tienen coordenadas GPS válidas para mostrar en un mapa interactivo.'
    )
    @action(detail=False, methods=['get'], url_path='mapa')
    def mapa(self, request):
        from django.db.models import Q
        casos = self.get_queryset().filter(
            latitud__isnull=False, longitud__isnull=False
        ).exclude(Q(latitud=0) | Q(longitud=0))
        serializer = CasoDetailSerializer(casos, many=True)
        return Response({
            'mensaje': 'Casos con coordenadas obtenidos correctamente',
            'data': serializer.data,
            'total': len(serializer.data)
        })
    
    @extend_schema(
        tags=['Casos'],
        summary='[WEB] Incrementar contador de compartidos',
        description='Roles: Cualquier usuario. Incrementa el contador cuando un usuario comparte el caso en redes sociales o mensajería.'
    )
    @action(detail=True, methods=['post'], url_path='compartir')
    def compartir(self, request, pk=None):
        caso = self.get_object()
        caso.compartido += 1
        caso.save(update_fields=['compartido'])
        return Response({'mensaje': 'Caso compartido correctamente', 'total_compartidos': caso.compartido})

    @extend_schema(
        tags=['Casos'],
        summary='[WEB] Obtener mis casos',
        description='Roles: Usuario autenticado (beneficiario). Lista todos los casos creados por el usuario autenticado actualmente.'
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='mis-casos')
    def mis_casos(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'No autenticado'}, status=401)
        casos = self.get_queryset().filter(id_beneficiario_id=user_id)
        serializer = CasoListSerializer(casos, many=True)
        return Response({'mensaje': 'Mis casos obtenidos correctamente', 'data': serializer.data})


@extend_schema_view(
    list=extend_schema(tags=['Estados de Caso'], summary='[WEB / WEB ADMIN] Listar estados', description='Retorna el catálogo de estados de caso (Pendiente, En progreso, Completado, etc).'),
    create=extend_schema(tags=['Estados de Caso'], summary='[WEB ADMIN] Crear estado'),
    retrieve=extend_schema(tags=['Estados de Caso'], summary='[WEB ADMIN] Obtener estado por ID'),
    update=extend_schema(tags=['Estados de Caso'], summary='[WEB ADMIN] Actualizar estado'),
    partial_update=extend_schema(tags=['Estados de Caso'], summary='[WEB ADMIN] Actualizar estado parcial'),
    destroy=extend_schema(tags=['Estados de Caso'], summary='[WEB ADMIN] Eliminar estado'),
)
class EstadoCasoViewSet(viewsets.ModelViewSet):
    queryset = EstadoCaso.objects.all()
    serializer_class = EstadoCasoSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['Categorías'], summary='[WEB / WEB ADMIN] Listar categorías', description='Retorna el catálogo de categorías activas (Alimentación, Salud, Vivienda, Educación, etc).'),
    create=extend_schema(tags=['Categorías'], summary='[WEB ADMIN] Crear categoría'),
    retrieve=extend_schema(tags=['Categorías'], summary='[WEB / WEB ADMIN] Obtener categoría por ID'),
    update=extend_schema(tags=['Categorías'], summary='[WEB ADMIN] Actualizar categoría'),
    partial_update=extend_schema(tags=['Categorías'], summary='[WEB ADMIN] Actualizar categoría parcial'),
    destroy=extend_schema(tags=['Categorías'], summary='[WEB ADMIN] Eliminar categoría'),
)
class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Categorias.objects.filter(es_activo=True)
    
    @extend_schema(
        tags=['Categorías'],
        summary='[WEB / WEB ADMIN] Obtener casos de una categoría',
        description='Retorna todos los casos asociados a una categoría específica.'
    )
    @action(detail=True, methods=['get'], url_path='casos')
    def casos(self, request, pk=None):
        categoria = self.get_object()
        casos_ids = CasoCategorias.objects.filter(id_categoria=categoria).values_list('id_caso_id', flat=True)
        casos = Casos.objects.filter(id__in=casos_ids)
        serializer = CasoListSerializer(casos, many=True)
        return Response({'mensaje': 'Casos de la categoría obtenidos correctamente', 'data': serializer.data})


@extend_schema_view(
    list=extend_schema(tags=['Caso-Categorías'], summary='[WEB ADMIN] Listar relaciones caso-categoría'),
    create=extend_schema(tags=['Caso-Categorías'], summary='[WEB ADMIN] Asignar categoría a caso'),
    retrieve=extend_schema(tags=['Caso-Categorías'], summary='[WEB ADMIN] Obtener relación por ID'),
    destroy=extend_schema(tags=['Caso-Categorías'], summary='[WEB ADMIN] Eliminar categoría de caso'),
)
class CasoCategoriaViewSet(viewsets.ModelViewSet):
    queryset = CasoCategorias.objects.all()
    serializer_class = CasoCategoriaSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['Donaciones'], summary='[WEB / WEB ADMIN] Listar donaciones'),
    create=extend_schema(
        tags=['Donaciones'],
        summary='[WEB] Crear donación',
        description='Roles: Usuario autenticado (donador). Registra una donación económica o en especie para un caso específico.',
        examples=[
            OpenApiExample(
                'Crear donación',
                value={
                    "id_caso": 1,
                    "monto": 500.00,
                    "metodo_pago": "Transferencia",
                    "es_anonima": False,
                    "mensaje_donador": "Espero que esto ayude a la familia"
                }
            )
        ]
    ),
    retrieve=extend_schema(tags=['Donaciones'], summary='[WEB / WEB ADMIN] Obtener donación por ID'),
    update=extend_schema(tags=['Donaciones'], summary='[WEB ADMIN] Actualizar donación'),
    partial_update=extend_schema(tags=['Donaciones'], summary='[WEB ADMIN] Actualizar donación parcial'),
    destroy=extend_schema(tags=['Donaciones'], summary='[WEB ADMIN] Eliminar donación'),
)
class DonacionViewSet(viewsets.ModelViewSet):
    serializer_class = DonacionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Donaciones.objects.select_related('id_donador', 'id_caso').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DonacionCreateSerializer
        return DonacionSerializer
    
    @extend_schema(tags=['Donaciones'], summary='[WEB] Obtener mis donaciones', description='Roles: Usuario autenticado (donador). Lista todas las donaciones realizadas por el usuario.')
    @action(detail=False, methods=['get'], url_path='mis-donaciones')
    def mis_donaciones(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'No autenticado'}, status=401)
        donaciones = self.get_queryset().filter(id_donador_id=user_id)
        serializer = self.get_serializer(donaciones, many=True)
        return Response({'mensaje': 'Mis donaciones obtenidas correctamente', 'data': serializer.data})


@extend_schema_view(
    list=extend_schema(tags=['Evidencias'], summary='[WEB / WEB ADMIN] Listar evidencias'),
    create=extend_schema(tags=['Evidencias'], summary='[WEB] Subir evidencia', description='Roles: Usuario autenticado. Sube evidencias fotográficas o documentales de un caso.'),
    retrieve=extend_schema(tags=['Evidencias'], summary='[WEB / WEB ADMIN] Obtener evidencia por ID'),
    update=extend_schema(tags=['Evidencias'], summary='[WEB ADMIN] Actualizar evidencia'),
    partial_update=extend_schema(tags=['Evidencias'], summary='[WEB ADMIN] Actualizar evidencia parcial'),
    destroy=extend_schema(tags=['Evidencias'], summary='[WEB / WEB ADMIN] Eliminar evidencia'),
)
class EvidenciaViewSet(viewsets.ModelViewSet):
    queryset = Evidencias.objects.all()
    serializer_class = EvidenciaSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Conversaciones'], summary='[WEB] Listar mis conversaciones'),
    create=extend_schema(tags=['Conversaciones'], summary='[WEB] Crear conversación'),
    retrieve=extend_schema(tags=['Conversaciones'], summary='[WEB] Obtener conversación por ID'),
    destroy=extend_schema(tags=['Conversaciones'], summary='[WEB] Eliminar conversación'),
)
class ConversacionViewSet(viewsets.ModelViewSet):
    queryset = Conversaciones.objects.all()
    serializer_class = ConversacionSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Mensajes'], summary='[WEB] Listar mensajes'),
    create=extend_schema(tags=['Mensajes'], summary='[WEB] Enviar mensaje'),
    retrieve=extend_schema(tags=['Mensajes'], summary='[WEB] Obtener mensaje por ID'),
    update=extend_schema(tags=['Mensajes'], summary='[WEB] Actualizar mensaje'),
    destroy=extend_schema(tags=['Mensajes'], summary='[WEB] Eliminar mensaje'),
)
class MensajeViewSet(viewsets.ModelViewSet):
    queryset = Mensajes.objects.all()
    serializer_class = MensajeSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Tipos de Mensaje'], summary='[WEB ADMIN] Listar tipos'),
    create=extend_schema(tags=['Tipos de Mensaje'], summary='[WEB ADMIN] Crear tipo'),
    retrieve=extend_schema(tags=['Tipos de Mensaje'], summary='[WEB ADMIN] Obtener tipo por ID'),
    update=extend_schema(tags=['Tipos de Mensaje'], summary='[WEB ADMIN] Actualizar tipo'),
    partial_update=extend_schema(tags=['Tipos de Mensaje'], summary='[WEB ADMIN] Actualizar tipo parcial'),
    destroy=extend_schema(tags=['Tipos de Mensaje'], summary='[WEB ADMIN] Eliminar tipo'),
)
class TipoMensajeViewSet(viewsets.ModelViewSet):
    queryset = TipoMensaje.objects.all()
    serializer_class = TipoMensajeSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['Reportes'], summary='[WEB ADMIN] Listar reportes'),
    create=extend_schema(tags=['Reportes'], summary='[WEB] Crear reporte', description='Roles: Usuario autenticado. Reporta comportamiento inapropiado o fraudulento de otro usuario o caso.'),
    retrieve=extend_schema(tags=['Reportes'], summary='[WEB ADMIN] Obtener reporte por ID'),
    update=extend_schema(tags=['Reportes'], summary='[WEB ADMIN] Actualizar reporte'),
    partial_update=extend_schema(tags=['Reportes'], summary='[WEB ADMIN] Actualizar reporte parcial'),
    destroy=extend_schema(tags=['Reportes'], summary='[WEB ADMIN] Eliminar reporte'),
)
class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reportes.objects.all()
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Estados de Reporte'], summary='[WEB ADMIN] Listar estados'),
    create=extend_schema(tags=['Estados de Reporte'], summary='[WEB ADMIN] Crear estado'),
    retrieve=extend_schema(tags=['Estados de Reporte'], summary='[WEB ADMIN] Obtener estado por ID'),
    update=extend_schema(tags=['Estados de Reporte'], summary='[WEB ADMIN] Actualizar estado'),
    partial_update=extend_schema(tags=['Estados de Reporte'], summary='[WEB ADMIN] Actualizar estado parcial'),
    destroy=extend_schema(tags=['Estados de Reporte'], summary='[WEB ADMIN] Eliminar estado'),
)
class EstadoReporteViewSet(viewsets.ModelViewSet):
    queryset = EstadoReporte.objects.all()
    serializer_class = EstadoReporteSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['Sanciones'], summary='[WEB ADMIN] Listar sanciones'),
    create=extend_schema(tags=['Sanciones'], summary='[WEB ADMIN] Crear sanción'),
    retrieve=extend_schema(tags=['Sanciones'], summary='[WEB ADMIN] Obtener sanción por ID'),
    update=extend_schema(tags=['Sanciones'], summary='[WEB ADMIN] Actualizar sanción'),
    partial_update=extend_schema(tags=['Sanciones'], summary='[WEB ADMIN] Actualizar sanción parcial'),
    destroy=extend_schema(tags=['Sanciones'], summary='[WEB ADMIN] Eliminar sanción'),
)
class SancionViewSet(viewsets.ModelViewSet):
    queryset = Sanciones.objects.all()
    serializer_class = SancionSerializer
    permission_classes = [IsAdminUser]


@extend_schema_view(
    list=extend_schema(tags=['Tipos de Sanción'], summary='[WEB ADMIN] Listar tipos'),
    create=extend_schema(tags=['Tipos de Sanción'], summary='[WEB ADMIN] Crear tipo'),
    retrieve=extend_schema(tags=['Tipos de Sanción'], summary='[WEB ADMIN] Obtener tipo por ID'),
    update=extend_schema(tags=['Tipos de Sanción'], summary='[WEB ADMIN] Actualizar tipo'),
    partial_update=extend_schema(tags=['Tipos de Sanción'], summary='[WEB ADMIN] Actualizar tipo parcial'),
    destroy=extend_schema(tags=['Tipos de Sanción'], summary='[WEB ADMIN] Eliminar tipo'),
)
class TipoSancionViewSet(viewsets.ModelViewSet):
    queryset = TipoSancion.objects.all()
    serializer_class = TipoSancionSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['Documentos OCR'], summary='[WEB ADMIN] Listar documentos OCR'),
    create=extend_schema(tags=['Documentos OCR'], summary='[WEB] Subir documento para OCR', description='Roles: Usuario autenticado. Sube documentos de identificación (INE) para validación automática mediante OCR.'),
    retrieve=extend_schema(tags=['Documentos OCR'], summary='[WEB / WEB ADMIN] Obtener documento por ID'),
    update=extend_schema(tags=['Documentos OCR'], summary='[WEB ADMIN] Actualizar documento'),
    partial_update=extend_schema(tags=['Documentos OCR'], summary='[WEB ADMIN] Actualizar documento parcial'),
    destroy=extend_schema(tags=['Documentos OCR'], summary='[WEB ADMIN] Eliminar documento'),
)
class DocumentoOCRViewSet(viewsets.ModelViewSet):
    queryset = DocumentosOCR.objects.all()
    serializer_class = DocumentoOCRSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Estados OCR'], summary='[WEB ADMIN] Listar estados'),
    create=extend_schema(tags=['Estados OCR'], summary='[WEB ADMIN] Crear estado'),
    retrieve=extend_schema(tags=['Estados OCR'], summary='[WEB ADMIN] Obtener estado por ID'),
    update=extend_schema(tags=['Estados OCR'], summary='[WEB ADMIN] Actualizar estado'),
    partial_update=extend_schema(tags=['Estados OCR'], summary='[WEB ADMIN] Actualizar estado parcial'),
    destroy=extend_schema(tags=['Estados OCR'], summary='[WEB ADMIN] Eliminar estado'),
)
class EstadoOCRViewSet(viewsets.ModelViewSet):
    queryset = EstadoOCR.objects.all()
    serializer_class = EstadoOCRSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(tags=['Log OCR'], summary='[WEB ADMIN] Listar logs de procesamiento OCR'),
    retrieve=extend_schema(tags=['Log OCR'], summary='[WEB ADMIN] Obtener log por ID'),
)
class LogOCRViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogOCR.objects.all()
    serializer_class = LogOCRSerializer
    permission_classes = [IsAdminUser]