from django.urls import path
from django.views.generic import TemplateView

app_name = 'web'

urlpatterns = [
    # Páginas públicas
    path('', TemplateView.as_view(template_name='web/inicio.html'), name='inicio'),
    path('login/', TemplateView.as_view(template_name='web/login.html'), name='login'),
    path('registro/', TemplateView.as_view(template_name='web/registro.html'), name='registro'),
    path('casos/', TemplateView.as_view(template_name='web/casos.html'), name='casos'),
    path('casos/<int:pk>/', TemplateView.as_view(template_name='web/caso_detalle.html'), name='caso_detalle'),
    path('mapa/', TemplateView.as_view(template_name='web/mapa.html'), name='mapa'),
    path('nosotros/', TemplateView.as_view(template_name='web/nosotros.html'), name='nosotros'),
    path('contacto/', TemplateView.as_view(template_name='web/contacto.html'), name='contacto'),
    
    # Páginas de usuario autenticado
    path('perfil/', TemplateView.as_view(template_name='web/perfil.html'), name='perfil'),
    path('mis-casos/', TemplateView.as_view(template_name='web/mis_casos.html'), name='mis_casos'),
    path('mis-donaciones/', TemplateView.as_view(template_name='web/mis_donaciones.html'), name='mis_donaciones'),
    path('mensajes/', TemplateView.as_view(template_name='web/mensajes.html'), name='mensajes'),
]