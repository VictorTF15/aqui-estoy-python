from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import *
# Eliminamos la importación de web_views si no la estamos usando, 
# para evitar que cargue archivos con errores.

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
# ... (mantén todos tus router.register aquí)
router.register(r'log-ocr', LogOCRViewSet, basename='logocr')

app_name = 'members'

urlpatterns = [
    # Solo dejamos la API por ahora para asegurar que el server levante
    path('api/', include(router.urls)),
]