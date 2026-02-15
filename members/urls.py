from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    # Página principal
    path('', views.feed, name='index'),
    
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Feed
    path('feed/', views.feed, name='feed'),
    path('mapa/', views.mapa_casos, name='mapa_casos'),
    
    # Casos
    path('casos/', views.lista_casos, name='lista_casos'),
    path('casos/crear/', views.crear_caso, name='crear_caso'),
    path('casos/<int:caso_id>/', views.detalle_caso, name='detalle_caso'),
    path('casos/<int:caso_id>/editar/', views.editar_caso, name='editar_caso'),  # AGREGAR ESTA LÍNEA
    path('mis-casos/', views.mis_casos, name='mis_casos'),
    path('casos/<int:caso_id>/compartir/', views.compartir_caso, name='compartir_caso'),
    
    # Donaciones
    path('donaciones/', views.lista_donaciones, name='lista_donaciones'),
    path('donaciones/crear/<int:caso_id>/', views.crear_donacion, name='crear_donacion'),
    
    # Usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/<int:user_id>/', views.perfil_usuario, name='perfil_usuario'),
    path('usuarios/<int:user_id>/datos/', views.obtener_datos_usuario, name='obtener_datos_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/crear-modal/', views.crear_usuario_modal, name='crear_usuario_modal'),
    
    # Categorías
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    
    # API
    path('api/casos-mapa/', views.api_casos_mapa, name='api_casos_mapa'),
    
    # Admin
    # path('admin/', views.admin, name='admin'),  # ← COMENTAR ESTA LÍNEA
]