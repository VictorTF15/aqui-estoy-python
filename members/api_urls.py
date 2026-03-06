from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from . import api_views

# Router para ViewSets
router = DefaultRouter()
router.register(r'usuarios', api_views.UsuarioViewSet, basename='usuario')
router.register(r'casos', api_views.CasoViewSet, basename='caso')
router.register(r'donaciones', api_views.DonacionViewSet, basename='donacion')
router.register(r'categorias', api_views.CategoriaViewSet, basename='categoria')
router.register(r'estados', api_views.EstadoCasoViewSet, basename='estado')

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Aquí Estoy API",
        default_version='v1',
        description="API REST para la plataforma de donaciones Aquí Estoy",
        contact=openapi.Contact(email="contact@aquiestoy.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Documentación Swagger con drf-yasg
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Autenticación JWT (opcional)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Rutas del router
    path('', include(router.urls)),
]