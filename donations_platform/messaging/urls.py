from django.urls import path
from . import views

urlpatterns = [
    path('conversaciones/', views.ConversacionesListView.as_view(), name='conversaciones_list'),
    path('conversacion/<int:pk>/', views.ConversacionDetailView.as_view(), name='conversacion_detail'),
    path('conversacion/<int:pk>/nuevo_mensaje/', views.NuevoMensajeView.as_view(), name='nuevo_mensaje'),
]