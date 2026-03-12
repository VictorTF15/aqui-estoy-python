from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

urlpatterns = [
    # 1. Redirección de Raíz a Swagger
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
    
    # 2. Admin de Django
    path('admin/', admin.site.urls),
    
    # 3. Documentación DRF-Spectacular (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # 4. Inclusión de las rutas de la App Members
    path('', include('members.urls')),
]