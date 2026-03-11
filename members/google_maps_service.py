import googlemaps
from django.conf import settings
import os


class GoogleMapsService:
    """Servicio para interactuar con Google Maps Geocoding API"""
    
    def __init__(self):
        # Obtener API key desde settings o variable de entorno
        self.api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None) or os.getenv('GOOGLE_MAPS_API_KEY')
        
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY no está configurada")
        
        # Inicializar cliente de Google Maps
        self.gmaps = googlemaps.Client(key=self.api_key)
    
    def obtener_coordenadas(self, direccion):
        """
        Obtener coordenadas de una dirección usando Google Maps Geocoding
        
        Args:
            direccion: Dirección completa
            
        Returns:
            dict: {'lat': float, 'lng': float, 'nombre': str, 'direccion': str} o None
        """
        try:
            # Geocodificar la dirección
            resultado = self.gmaps.geocode(direccion, region='mx', language='es')
            
            if resultado and len(resultado) > 0:
                primer_resultado = resultado[0]
                location = primer_resultado['geometry']['location']
                
                return {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'nombre': primer_resultado.get('formatted_address', ''),
                    'direccion': primer_resultado.get('formatted_address', ''),
                    'place_id': primer_resultado.get('place_id', '')
                }
            
            return None
            
        except Exception as e:
            print(f"Error en geocodificación con Google Maps: {e}")
            return None
    
    def obtener_direccion(self, lat, lng):
        """
        Obtener dirección desde coordenadas (Reverse Geocoding)
        
        Args:
            lat: Latitud
            lng: Longitud
            
        Returns:
            str: Dirección formateada o None
        """
        try:
            resultado = self.gmaps.reverse_geocode((lat, lng), language='es')
            
            if resultado and len(resultado) > 0:
                return resultado[0].get('formatted_address', None)
            
            return None
            
        except Exception as e:
            print(f"Error en reverse geocoding: {e}")
            return None
    
    def geocodificar_casos(self, casos):
        """
        Geocodificar múltiples casos que no tienen coordenadas
        
        Args:
            casos: QuerySet de casos
            
        Returns:
            int: Número de casos actualizados
        """
        casos_actualizados = 0
        
        for caso in casos:
            if not caso.latitud or not caso.longitud:
                # Construir dirección completa
                direccion_parts = []
                
                if caso.ciudad:
                    direccion_parts.append(caso.ciudad)
                if caso.estado:
                    direccion_parts.append(caso.estado)
                direccion_parts.append("México")
                
                direccion = ", ".join(direccion_parts)
                
                # Obtener coordenadas
                coords = self.obtener_coordenadas(direccion)
                
                if coords:
                    caso.latitud = coords['lat']
                    caso.longitud = coords['lng']
                    caso.save()
                    casos_actualizados += 1
                    print(f"✓ Caso '{caso.titulo}' geocodificado: {coords['lat']}, {coords['lng']}")
                else:
                    print(f"✗ No se pudieron obtener coordenadas para: {direccion}")
        
        return casos_actualizados
    
    def buscar_lugares(self, query, location=None, radius=50000):
        """
        Buscar lugares usando Google Places API
        
        Args:
            query: Término de búsqueda
            location: Tupla (lat, lng) para búsqueda cercana
            radius: Radio de búsqueda en metros (default 50km)
            
        Returns:
            list: Lista de lugares encontrados
        """
        try:
            if location:
                resultado = self.gmaps.places_nearby(
                    location=location,
                    radius=radius,
                    keyword=query,
                    language='es'
                )
            else:
                resultado = self.gmaps.places(
                    query=query,
                    region='mx',
                    language='es'
                )
            
            if resultado and 'results' in resultado:
                lugares = []
                for lugar in resultado['results']:
                    lugares.append({
                        'nombre': lugar.get('name', ''),
                        'direccion': lugar.get('formatted_address', lugar.get('vicinity', '')),
                        'lat': lugar['geometry']['location']['lat'],
                        'lng': lugar['geometry']['location']['lng'],
                        'place_id': lugar.get('place_id', '')
                    })
                return lugares
            
            return []
            
        except Exception as e:
            print(f"Error en búsqueda de lugares: {e}")
            return []