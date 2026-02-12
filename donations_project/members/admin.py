from django.contrib import admin
from .models import Usuario, Caso, Donacion, Categoria

admin.site.register(Usuario)
admin.site.register(Caso)
admin.site.register(Donacion)
admin.site.register(Categoria)