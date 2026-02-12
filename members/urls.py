from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    # Home y Feed
    path('', views.feed, name='index'),
    path('feed/', views.feed, name='feed'),
    
    # Casos
    path('casos/', views.lista_casos, name='lista_casos'),
    path('casos/crear/', views.crear_caso, name='crear_caso'),
    path('casos/<int:caso_id>/', views.detalle_caso, name='detalle_caso'),
    path('casos/<int:caso_id>/editar/', views.editar_caso, name='editar_caso'),
    
    # Donaciones
    path('donaciones/', views.lista_donaciones, name='lista_donaciones'),
    path('casos/<int:caso_id>/donar/', views.crear_donacion, name='crear_donacion'),
    
    # Usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/<int:user_id>/', views.perfil_usuario, name='perfil_usuario'),
    path('usuarios/<int:user_id>/datos/', views.obtener_datos_usuario, name='obtener_datos_usuario'),
    path('usuarios/modal/crear-editar/', views.crear_usuario_modal, name='crear_usuario_modal'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/registro/', views.register, name='register'),
    path('usuarios/login/', views.login_view, name='login'),
    path('usuarios/logout/', views.logout_view, name='logout'),
    
    # Categorías
    path('categorias/', views.lista_categorias, name='lista_categorias'),
]