from django.contrib import admin
from .models import Conversacion, Mensaje

@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_usuario1', 'id_usuario2', 'fecha_creacion', 'esta_activa')
    search_fields = ('id_usuario1__nombres', 'id_usuario2__nombres')
    list_filter = ('esta_activa',)

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_conversacion', 'id_emisor', 'fecha_envio', 'es_leido')
    search_fields = ('contenido', 'id_emisor__nombres')
    list_filter = ('es_leido',)