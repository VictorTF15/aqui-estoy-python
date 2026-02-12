from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.feed, name='index'),
    path('feed/', views.feed, name='feed'),
    path('casos/', views.lista_casos, name='lista_casos'),
    path('casos/crear/', views.crear_caso, name='crear_caso'),
    path('casos/<int:caso_id>/', views.detalle_caso, name='detalle_caso'),
    path('donaciones/', views.lista_donaciones, name='lista_donaciones'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/registro/', views.register, name='register'),   # <- asegurarse que existe
    path('usuarios/login/', views.login_view, name='login'),
    path('usuarios/logout/', views.logout_view, name='logout'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
]