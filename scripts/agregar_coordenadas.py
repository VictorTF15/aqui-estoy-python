import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion_inicial.settings')
django.setup()

from members.models import Casos

def agregar_coordenadas():
    """
    Agrega coordenadas a los casos basándose en su ID y colonia
    Las coordenadas corresponden a ubicaciones reales de Puebla
    """
    
    # Mapeo de casos con sus coordenadas reales
    coordenadas_casos = {
        3: {  # Santiago - Apoyo con ropa de invierno
            'latitud': 19.0414,
            'longitud': -98.2063,
            'colonia': 'Santiago'
        },
        4: {  # Analco - Medicamentos diabetes
            'latitud': 19.0444,
            'longitud': -98.1897,
            'colonia': 'Analco'
        },
        5: {  # Azcárate - Despensa básica
            'latitud': 19.0280,
            'longitud': -98.2180,
            'colonia': 'Azcárate'
        },
        6: {  # Humboldt - Útiles escolares
            'latitud': 19.0470,
            'longitud': -98.1935,
            'colonia': 'Humboldt'
        },
        7: {  # El Carmen - Reparación techo
            'latitud': 19.0356,
            'longitud': -98.1823,
            'colonia': 'El Carmen'
        },
        8: {  # La Paz - Alimentos adulto mayor
            'latitud': 19.0525,
            'longitud': -98.2120,
            'colonia': 'La Paz'
        },
        9: {  # Amor - Silla de ruedas
            'latitud': 19.0280,
            'longitud': -98.2180,
            'colonia': 'Amor'
        },
        10: {  # Angelópolis - Andadera
            'latitud': 19.0050,
            'longitud': -98.2450,
            'colonia': 'Angelópolis'
        }
    }
    
    print("=" * 60)
    print("SCRIPT DE ACTUALIZACIÓN DE COORDENADAS")
    print("=" * 60)
    print()
    
    casos_actualizados = 0
    casos_no_encontrados = []
    
    for caso_id, datos in coordenadas_casos.items():
        try:
            caso = Casos.objects.get(id=caso_id)
            
            # Actualizar coordenadas
            caso.latitud = datos['latitud']
            caso.longitud = datos['longitud']
            caso.save(update_fields=['latitud', 'longitud'])
            
            casos_actualizados += 1
            print(f"✓ Caso #{caso_id} actualizado")
            print(f"  Título: {caso.titulo[:50]}...")
            print(f"  Colonia: {datos['colonia']}")
            print(f"  Coordenadas: ({datos['latitud']}, {datos['longitud']})")
            print()
            
        except Casos.DoesNotExist:
            casos_no_encontrados.append(caso_id)
            print(f"✗ Caso #{caso_id} no encontrado en la base de datos")
            print()
    
    # Resumen
    print("=" * 60)
    print("RESUMEN DE ACTUALIZACIÓN")
    print("=" * 60)
    print(f"✓ Casos actualizados correctamente: {casos_actualizados}")
    
    if casos_no_encontrados:
        print(f"✗ Casos no encontrados: {len(casos_no_encontrados)}")
        print(f"  IDs: {', '.join(map(str, casos_no_encontrados))}")
    
    print()
    
    # Verificar casos con coordenadas
    print("=" * 60)
    print("VERIFICACIÓN DE CASOS CON COORDENADAS")
    print("=" * 60)
    
    casos_con_coords = Casos.objects.filter(
        latitud__isnull=False,
        longitud__isnull=False,
        esta_abierto=True
    ).exclude(
        latitud=0,
        longitud=0
    ).order_by('id')
    
    print(f"\nTotal de casos con coordenadas válidas: {casos_con_coords.count()}")
    print()
    
    for caso in casos_con_coords:
        estado = caso.id_estado.nombre if caso.id_estado else 'Sin estado'
        print(f"  #{caso.id} - {caso.titulo[:50]}...")
        print(f"         Colonia: {caso.colonia}")
        print(f"         Coordenadas: ({caso.latitud}, {caso.longitud})")
        print(f"         Estado: {estado}")
        print()
    
    # Verificar casos SIN coordenadas
    casos_sin_coords = Casos.objects.filter(
        esta_abierto=True
    ).filter(
        latitud__isnull=True
    ) | Casos.objects.filter(
        esta_abierto=True,
        latitud=0
    )
    
    if casos_sin_coords.exists():
        print("=" * 60)
        print("⚠️  CASOS SIN COORDENADAS")
        print("=" * 60)
        print(f"\nTotal de casos SIN coordenadas: {casos_sin_coords.count()}")
        print()
        
        for caso in casos_sin_coords:
            print(f"  #{caso.id} - {caso.titulo[:50]}...")
            print(f"         Colonia: {caso.colonia}")
            print()
    
    print("=" * 60)
    print("¡ACTUALIZACIÓN COMPLETADA!")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print("1. Reinicia el servidor Django: python manage.py runserver")
    print("2. Accede a http://127.0.0.1:8000/mapa/")
    print("3. Verifica que los marcadores aparezcan en el mapa")
    print()

if __name__ == '__main__':
    try:
        agregar_coordenadas()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)