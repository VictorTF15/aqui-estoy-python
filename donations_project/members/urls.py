from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('casos/', views.lista_casos, name='lista_casos'),
    path('casos/<int:id>/', views.detalle_caso, name='detalle_caso'),
    path('donaciones/', views.lista_donaciones, name='lista_donaciones'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
]