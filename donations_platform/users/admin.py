from django.contrib import admin
from .models import CustomUser, Role, Permission

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombres', 'apellido_paterno', 'correo', 'id_tipo_usuario', 'fecha_registro', 'esta_activo')
    search_fields = ('nombres', 'apellido_paterno', 'correo')
    list_filter = ('esta_activo', 'id_tipo_usuario')

class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Permission, PermissionAdmin)