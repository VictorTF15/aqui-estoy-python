from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from members.api_views import (
    CustomTokenObtainPairView,
    UsuarioViewSet, TipoUsuarioViewSet, CasoViewSet, EstadoCasoViewSet,
    CategoriaViewSet, CasoCategoriaViewSet, DonacionViewSet, EvidenciaViewSet,
    ConversacionViewSet, MensajeViewSet, TipoMensajeViewSet, ReporteViewSet,
    EstadoReporteViewSet, SancionViewSet, TipoSancionViewSet, DocumentoOCRViewSet,
    EstadoOCRViewSet, LogOCRViewSet
)

# Crear el router para las APIs
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'tipos-usuario', TipoUsuarioViewSet, basename='tipousuario')
router.register(r'casos', CasoViewSet, basename='caso')
router.register(r'estados-caso', EstadoCasoViewSet, basename='estadocaso')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'caso-categorias', CasoCategoriaViewSet, basename='casocategoria')
router.register(r'donaciones', DonacionViewSet, basename='donacion')
router.register(r'evidencias', EvidenciaViewSet, basename='evidencia')
router.register(r'conversaciones', ConversacionViewSet, basename='conversacion')
router.register(r'mensajes', MensajeViewSet, basename='mensaje')
router.register(r'tipos-mensaje', TipoMensajeViewSet, basename='tipomensaje')
router.register(r'reportes', ReporteViewSet, basename='reporte')
router.register(r'estados-reporte', EstadoReporteViewSet, basename='estadoreporte')
router.register(r'sanciones', SancionViewSet, basename='sancion')
router.register(r'tipos-sancion', TipoSancionViewSet, basename='tiposancion')
router.register(r'documentos-ocr', DocumentoOCRViewSet, basename='documentoocr')
router.register(r'estados-ocr', EstadoOCRViewSet, basename='estadoocr')
router.register(r'log-ocr', LogOCRViewSet, basename='logocr')

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # Autenticación JWT - AMBAS RUTAS
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair_alt'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Documentación de la API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Incluir las rutas de members (Web)
    path('', include('members.urls')),
]

# Servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)