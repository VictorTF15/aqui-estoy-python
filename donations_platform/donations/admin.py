from django.contrib import admin
from .models import Casos, Donaciones, CasoCategorias, Evidencias

@admin.register(Casos)
class CasosAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'id_beneficiario', 'id_estado', 'monto_objetivo', 'monto_recaudado', 'fecha_creacion')
    search_fields = ('titulo', 'id_beneficiario__nombres', 'id_beneficiario__apellido_paterno')
    list_filter = ('id_estado', 'fecha_creacion')

@admin.register(Donaciones)
class DonacionesAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_donador', 'id_caso', 'monto', 'fecha_compromiso', 'estado_donacion')
    search_fields = ('id_donador__nombres', 'id_caso__titulo')
    list_filter = ('estado_donacion', 'fecha_compromiso')

@admin.register(CasoCategorias)
class CasoCategoriasAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_caso', 'id_categoria', 'fecha_asignacion')
    search_fields = ('id_caso__titulo', 'id_categoria__nombre')

@admin.register(Evidencias)
class EvidenciasAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_caso', 'id_usuario', 'titulo', 'fecha_creacion', 'es_publico')
    search_fields = ('titulo', 'id_caso__titulo', 'id_usuario__nombres')
    list_filter = ('es_publico', 'fecha_creacion')