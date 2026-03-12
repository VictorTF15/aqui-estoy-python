from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import *
from .views import web_views 
from django.views.generic import RedirectView # Importante para la redirección

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
# ... (todos tus otros registros de router se mantienen igual)
router.register(r'log-ocr', LogOCRViewSet, basename='logocr')

app_name = 'members'

urlpatterns = [
    # API REST - Esta será tu ruta principal de datos
    path('api/', include(router.urls)),
    
    # Redirigir la raíz de esta app a la documentación global
    # (Asumiendo que Swagger está en el urls.py principal)
    path('', RedirectView.as_view(url='/api/schema/swagger-ui/', permanent=False)),
]