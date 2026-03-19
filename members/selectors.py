from typing import List, Dict, Any
from django.db.models import QuerySet
from .models import Casos, Donaciones

class CasoSelector:
    @staticmethod
    def get_casos_mapa() -> List[Dict[str, Any]]:
        """
        Retorna la lista de casos abiertos con coordenadas válidas para ser mostrados en el mapa.
        """
        casos = Casos.objects.filter(esta_abierto=True).exclude(latitud__isnull=True).exclude(longitud__isnull=True)
        return [{
            'id': caso.id,
            'titulo': caso.titulo,
            'latitud': float(caso.latitud),
            'longitud': float(caso.longitud),
            'prioridad': caso.prioridad,
        } for caso in casos]

    @staticmethod
    def get_estadisticas() -> Dict[str, int]:
        """
        Retorna estadísticas sobre el estado de los casos.
        """
        return {
            'total': Casos.objects.count(),
            'abiertos': Casos.objects.filter(esta_abierto=True).count(),
            'cerrados': Casos.objects.filter(esta_abierto=False).count(),
        }

class DonacionSelector:
    @staticmethod
    def get_donaciones_por_usuario(usuario_id: int) -> QuerySet:
        """
        Retorna el QuerySet de donaciones pertenecientes a un usuario.
        """
        return Donaciones.objects.filter(id_donador_id=usuario_id)
