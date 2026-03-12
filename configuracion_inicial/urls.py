from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Redirige la raíz a la ruta de docs que ya usas
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
    
    path('admin/', admin.site.urls),
    
    # Asegúrate de que drf_spectacular use la ruta 'api/docs/'
    path('api/docs/', include('drf_spectacular.urls')), 
    
    path('', include('members.urls')),
]