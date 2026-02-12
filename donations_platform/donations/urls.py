from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_donaciones, name='lista_donaciones'),
    path('detalle/<int:id>/', views.detalle_donacion, name='detalle_donacion'),
]