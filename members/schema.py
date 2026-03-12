from rest_framework import filters
from rest_framework.pagination import PageNumberPagination


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