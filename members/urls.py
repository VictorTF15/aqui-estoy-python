from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import *
from .views import web_views  # Importar el módulo web_views
from . import views

# Router para las APIs
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

app_name = 'members'

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
    
    # ========================================
    # VERSIÓN WEB (Usuarios Normales)
    # ========================================
    
    # Autenticación Web
    path('web/login/', web_views.login_view, name='login_web'),
    path('web/register/', web_views.register_view, name='register_web'),
    
    # Dashboard Web
    path('web/home/', web_views.home_web, name='home_web'),
    path('web/perfil/', web_views.perfil_web, name='perfil_web'),
    
    # Casos Web
    path('web/casos/', web_views.lista_casos_web, name='lista_casos_web'),
    path('web/casos/<int:id>/', web_views.detalle_caso_web, name='detalle_caso_web'),
    path('web/casos/crear/', web_views.crear_caso_web, name='crear_caso_web'),
    
    # Donaciones Web
    path('web/donaciones/', web_views.lista_donaciones_web, name='lista_donaciones_web'),
    path('web/donaciones/crear/<int:caso_id>/', web_views.crear_donacion_web, name='crear_donacion_web'),
    
    # ========================================
    # VERSIÓN ADMIN (Administradores) - COMENTADAS TEMPORALMENTE
    # ========================================
    
    # Descomentar cuando existan estas funciones en views.py
    # path('login/', views.login_view, name='login'),
    # path('register/', views.register, name='register'),
    # path('feed/', views.feed, name='feed'),
    
    # ========================================
    # PÁGINA PRINCIPAL
    # ========================================
    # path('', views.myfirst, name='myfirst'),  # Comentado temporalmente
    
    # Redirigir la raíz al login web temporalmente
    path('', web_views.login_view, name='home'),
]