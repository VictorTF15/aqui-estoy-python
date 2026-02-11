from django.contrib import admin
from .models import (
    Usuarios, TipoUsuario, Casos, Donaciones, Evidencias,
    Categorias, Conversaciones, Mensajes, Reportes, DocumentosOCR
)

@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombres', 'apellido_paterno', 'correo', 'id_tipo_usuario', 'esta_activo', 'fecha_registro')
    list_filter = ('id_tipo_usuario', 'esta_activo')
    search_fields = ('nombres', 'apellido_paterno', 'correo')
    ordering = ('-fecha_registro',)

# Registra modelos adicionales simples
admin.site.register(TipoUsuario)
admin.site.register(Categorias)
admin.site.register(Casos)
admin.site.register(Donaciones)
admin.site.register(Evidencias)
admin.site.register(Conversaciones)
admin.site.register(Mensajes)
admin.site.register(Reportes)
admin.site.register(DocumentosOCR)
