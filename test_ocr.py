import boto3
import re
from decouple import config

# 1. Configuración
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_REGION = "us-east-1"

# Inicializar cliente de AWS fuera de la función para reutilizar la conexión
client = boto3.client(
    'rekognition',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def probar_ocr_ine(ruta_imagen):
    print("--- Procesando imagen ---")
    try:
        # Mover la lectura del archivo dentro del try para capturar errores de lectura
        with open(ruta_imagen, 'rb') as image_file:
            imagen_bytes = image_file.read()

        print("--- Enviando a AWS Rekognition ---")
        response = client.detect_text(Image={'Bytes': imagen_bytes})
        detecciones = response['TextDetections']
        
        # Unimos todo el texto en un solo string (una sola vez)
        texto_completo = " ".join([d['DetectedText'] for d in detecciones if d['Type'] == 'LINE'])
        print(f"Texto extraído crudo: {texto_completo}\n")

        # 2. Lógica de Filtrado directo en el diccionario
        datos = {
            'curp': re.search(r'[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z\d]\d', texto_completo),
            'clave': re.search(r'[A-Z]{6}\d{8}[HM]\d{3}', texto_completo), # Corregido [H|M] a [HM]
            'cic': re.search(r'\b\d{9}\b', texto_completo),
            'ocr_id': re.search(r'\b\d{12,13}\b', texto_completo)
        }

        print("--- RESULTADOS FILTRADOS ---")
        print(f"CURP: {datos['curp'].group(0) if datos['curp'] else 'No encontrada'}")
        print(f"Clave Electoral: {datos['clave'].group(0) if datos['clave'] else 'No encontrada'}")
        print(f"CIC (Parte trasera): {datos['cic'].group(0) if datos['cic'] else 'No encontrado'}")
        print(f"OCR ID (Parte trasera): {datos['ocr_id'].group(0) if datos['ocr_id'] else 'No encontrado'}")

    except FileNotFoundError:
        print(f"Error: No se encontró la imagen en la ruta '{ruta_imagen}'")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    probar_ocr_ine('ine_prueba.png')