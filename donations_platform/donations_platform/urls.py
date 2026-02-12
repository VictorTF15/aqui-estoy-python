from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('donations/', include('donations.urls')),
    path('messaging/', include('messaging.urls')),
]