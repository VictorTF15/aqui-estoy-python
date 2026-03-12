from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class FiltroBusquedaEspanol(filters.SearchFilter):
    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": self.search_param,
                "required": False,
                "in": "query",
                "description": "Término de búsqueda.",
                "schema": {"type": "string"},
            },
        ]


class FiltroOrdenamientoEspanol(filters.OrderingFilter):
    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": self.ordering_param,
                "required": False,
                "in": "query",
                "description": "Campo por el cual ordenar resultados.",
                "schema": {"type": "string"},
            },
        ]


class PaginacionEspanol(PageNumberPagination):
    page_size = 10
    page_query_param = "page"

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": self.page_query_param,
                "required": False,
                "in": "query",
                "description": "Número de página del conjunto paginado.",
                "schema": {"type": "integer"},
            }
        ]


class SchemaAutoEspanol(AutoSchema):
    """Schema personalizado que traduce textos al español."""

    def get_operation_parameters(self, view, path, method):
        """Sobrescribe los parámetros con nombres en español."""
        parametros = super().get_operation_parameters(view, path, method)
        
        for param in parametros:
            # Traducir nombres de parámetros comunes
            if param.get('name') == 'id':
                param['description'] = 'Un valor entero único que identifica este recurso.'
            elif param.get('name') == 'page':
                param['description'] = 'Número de página dentro del conjunto paginado.'
            elif param.get('name') == 'search':
                param['description'] = 'Término de búsqueda.'
            elif param.get('name') == 'ordering':
                param['description'] = 'Campo por el cual ordenar los resultados.'
        
        return parametros

    def get_operation_summary_and_description(self, path, method, view, auto_schema=None):
        """Obtiene resumen y descripción de la operación."""
        summary, description = super().get_operation_summary_and_description(path, method, view, auto_schema)
        return summary, description

    def get_request_body(self, path, method, view):
        """Traduce los textos de request body."""
        request_body = super().get_request_body(path, method, view)
        return request_body

    def get_response_bodies(self, path, method, view, auto_schema=None):
        """Traduce respuestas."""
        responses = super().get_response_bodies(path, method, view, auto_schema)
        
        # Traducir códigos de respuesta
        respuestas_traducidas = {}
        for code, data in responses.items():
            if code == '200':
                respuestas_traducidas[code] = {**data, 'description': 'Solicitud exitosa.'}
            elif code == '201':
                respuestas_traducidas[code] = {**data, 'description': 'Recurso creado exitosamente.'}
            elif code == '204':
                respuestas_traducidas[code] = {**data, 'description': 'Sin contenido. Operación exitosa.'}
            elif code == '400':
                respuestas_traducidas[code] = {**data, 'description': 'Solicitud inválida. Verifica los datos enviados.'}
            elif code == '401':
                respuestas_traducidas[code] = {**data, 'description': 'No autenticado. Se requiere token JWT.'}
            elif code == '403':
                respuestas_traducidas[code] = {**data, 'description': 'Acceso denegado. No tienes permisos.'}
            elif code == '404':
                respuestas_traducidas[code] = {**data, 'description': 'Recurso no encontrado.'}
            elif code == '500':
                respuestas_traducidas[code] = {**data, 'description': 'Error interno del servidor.'}
            else:
                respuestas_traducidas[code] = data
        
        return respuestas_traducidas