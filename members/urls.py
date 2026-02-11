from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.index, name='index'),
    path('casos/', views.lista_casos, name='lista_casos'),
    path('casos/<int:caso_id>/', views.detalle_caso, name='detalle_caso'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('donaciones/', views.lista_donaciones, name='lista_donaciones'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
]