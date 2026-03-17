from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import (
    CustomTokenObtainPairView, UsuarioViewSet, TipoUsuarioViewSet,
    CasoViewSet, EstadoCasoViewSet, CategoriaViewSet, CasoCategoriaViewSet,
    DonacionViewSet, EvidenciaViewSet, ConversacionViewSet, MensajeViewSet,
    TipoMensajeViewSet, ReporteViewSet, EstadoReporteViewSet, SancionViewSet,
    TipoSancionViewSet, DocumentoOCRViewSet, EstadoOCRViewSet, LogOCRViewSet,
)

app_name = 'members' # Cambiado a 'members' para coincidir con tu app principal

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
router.register(r'tipos-usuario', TipoUsuarioViewSet, basename='tipos-usuario')
router.register(r'casos', CasoViewSet, basename='casos')
router.register(r'estados-caso', EstadoCasoViewSet, basename='estados-caso')
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'caso-categorias', CasoCategoriaViewSet, basename='caso-categorias')
router.register(r'donaciones', DonacionViewSet, basename='donaciones')
router.register(r'evidencias', EvidenciaViewSet, basename='evidencias')
router.register(r'conversaciones', ConversacionViewSet, basename='conversaciones')
router.register(r'mensajes', MensajeViewSet, basename='mensajes')
router.register(r'tipos-mensaje', TipoMensajeViewSet, basename='tipos-mensaje')
router.register(r'reportes', ReporteViewSet, basename='reportes')
router.register(r'estados-reporte', EstadoReporteViewSet, basename='estados-reporte')
router.register(r'sanciones', SancionViewSet, basename='sanciones')
router.register(r'tipos-sancion', TipoSancionViewSet, basename='tipos-sancion')
router.register(r'documentos-ocr', DocumentoOCRViewSet, basename='documentos-ocr')
router.register(r'estados-ocr', EstadoOCRViewSet, basename='estados-ocr')
router.register(r'logs-ocr', LogOCRViewSet, basename='logs-ocr')

urlpatterns = [
    # Autenticación (Rutas manuales)
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    
    # Endpoints generados por el Router
    path('api/', include(router.urls)),
]