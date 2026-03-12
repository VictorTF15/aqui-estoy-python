from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # 1. LA RAÍZ: Manda a Swagger directamente
    path('', RedirectView.as_view(url='/api/schema/swagger-ui/', permanent=False)),
    
    # 2. ADMIN: Panel de control de Django
    path('admin/', admin.site.urls),
    
    # 3. ESQUEMA API: Lo que genera la documentación
    path('api/schema/', include('drf_spectacular.urls')),
    
    # 4. MEMBERS: Incluye todo lo de tu app
    path('', include('members.urls')),
]