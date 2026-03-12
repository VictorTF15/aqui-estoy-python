from drf_spectacular.views import SpectacularSwaggerView
from django.utils.translation import gettext_lazy as _


class SpectacularSwaggerViewEspanol(SpectacularSwaggerView):
    """Vista personalizada de Swagger UI en español."""
    
    template_name = 'swagger-ui-espanol.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['swagger_ui_settings'] = {
            'deepLinking': True,
            'presets': [
                'swaggerUIBundle.presets.apis',
                'swaggerUIBundle.SwaggerUIStandalonePreset'
            ],
            'layout': 'BaseLayout',
            'plugins': [
                'swaggerUIBundle.plugins.DownloadUrl'
            ],
        }
        return context