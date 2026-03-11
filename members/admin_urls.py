from django.urls import path
from django.views.generic import TemplateView

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard principal
    path('', TemplateView.as_view(template_name='admin/dashboard.html'), name='dashboard'),
    
    # Usuarios
    path('usuarios/', TemplateView.as_view(template_name='admin/usuarios/lista.html'), name='usuarios_lista'),
    path('usuarios/<int:pk>/', TemplateView.as_view(template_name='admin/usuarios/detalle.html'), name='usuarios_detalle'),
    
    # Casos
    path('casos/', TemplateView.as_view(template_name='admin/casos/lista.html'), name='casos_lista'),
    path('casos/crear/', TemplateView.as_view(template_name='admin/casos/crear.html'), name='casos_crear'),
    path('casos/<int:pk>/', TemplateView.as_view(template_name='admin/casos/detalle.html'), name='casos_detalle'),
    path('casos/<int:pk>/editar/', TemplateView.as_view(template_name='admin/casos/editar.html'), name='casos_editar'),
    
    # Categorías
    path('categorias/', TemplateView.as_view(template_name='admin/categorias/lista.html'), name='categorias_lista'),
    
    # Donaciones
    path('donaciones/', TemplateView.as_view(template_name='admin/donaciones/lista.html'), name='donaciones_lista'),
    
    # Reportes
    path('reportes/', TemplateView.as_view(template_name='admin/reportes/lista.html'), name='reportes_lista'),
    
    # Sanciones
    path('sanciones/', TemplateView.as_view(template_name='admin/sanciones/lista.html'), name='sanciones_lista'),
    
    # Mapa
    path('mapa/', TemplateView.as_view(template_name='admin/mapa.html'), name='mapa'),
    
    # Configuración
    path('configuracion/', TemplateView.as_view(template_name='admin/configuracion.html'), name='configuracion'),
]
