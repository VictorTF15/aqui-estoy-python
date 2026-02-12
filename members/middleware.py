from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class SessionAuthMiddleware:
    """
    Middleware que verifica automáticamente la sesión del usuario
    y agrega información del usuario al request.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs públicas que no requieren autenticación
        self.public_urls = [
            reverse('members:login'),
            reverse('members:register'),
            '/admin/',
            '/static/',
        ]
    
    def __call__(self, request):
        # Agregar información de usuario al request si existe sesión
        if request.session.get('user_id'):
            request.user_id = request.session.get('user_id')
            request.user_name = request.session.get('user_name', '')
            request.user_role = request.session.get('user_role', '')
            request.is_authenticated = True
        else:
            request.is_authenticated = False
        
        response = self.get_response(request)
        return response
    
    def is_public_url(self, path):
        """Verifica si la URL es pública"""
        for public_url in self.public_urls:
            if path.startswith(public_url):
                return True
        return False