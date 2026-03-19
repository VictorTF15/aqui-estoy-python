from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db import transaction
import time
import re
import boto3
from decouple import config
from .models import (
    Usuarios, DocumentosOCR, EstadoOCR, LogOCR, Casos, CasoCategorias
)

class UsuarioService:
    @staticmethod
    def cambiar_password(usuario: Usuarios, password_actual: str, password_nueva: str) -> bool:
        """
        Cambia la contraseña de un usuario validando la contraseña actual.
        Retorna True si fue exitoso, lanza ValueError si falla.
        """
        if not usuario.check_password(password_actual):
            raise ValueError('Contraseña incorrecta')
        
        usuario.contrasena = make_password(password_nueva)
        usuario.save(update_fields=['contrasena'])
        return True

class DocumentoOCRService:
    _CURP_REGEX = re.compile(r'[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z\d]\d')
    _CLAVE_ELECTOR_REGEX = re.compile(r'[A-Z]{6}\d{8}[HM]\d{3}')
    _CIC_REGEX = re.compile(r'IDMEX\s*(\d{9})', re.IGNORECASE)
    _CIC_FALLBACK_REGEX = re.compile(r'\b\d{9}\b')
    _OCR_ID_CR_REGEX = re.compile(r'\b\d{12,13}\b')
    _FECHA_NAC_REGEX = re.compile(r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b')
    _SEXO_REGEX = re.compile(r'\b(H|M)\b')
    _VIGENCIA_REGEX = re.compile(r'\b(\d{4})\s*[–\-]\s*(\d{4})\b')

    @classmethod
    def _get_rekognition_client(cls):
        return boto3.client(
            'rekognition',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name="us-east-1"
        )

    @classmethod
    def _extraer_nombre_apellidos(cls, texto):
        lineas = [linea.strip() for linea in texto.split(' ') if linea.strip()]
        candidatos = [p for p in lineas if p.isalpha() and len(p) > 2]
        if not candidatos:
            return None, None, None
        nombre = candidatos[0] if len(candidatos) >= 1 else None
        apellido_paterno = candidatos[1] if len(candidatos) >= 2 else None
        apellido_materno = candidatos[2] if len(candidatos) >= 3 else None
        return nombre, apellido_paterno, apellido_materno

    @classmethod
    def _extraer_datos_ocr(cls, imagen_bytes):
        start_time = time.perf_counter()
        client = cls._get_rekognition_client()
        response = client.detect_text(Image={'Bytes': imagen_bytes})
        detecciones = response.get('TextDetections', [])
        lineas = [d.get('DetectedText', '') for d in detecciones if d.get('Type') == 'LINE']
        texto_detectado = ' '.join(lineas)

        nombre, apellido_paterno, apellido_materno = cls._extraer_nombre_apellidos(texto_detectado)
        curp_match = cls._CURP_REGEX.search(texto_detectado)
        clave_match = cls._CLAVE_ELECTOR_REGEX.search(texto_detectado)
        
        cic_match = cls._CIC_REGEX.search(texto_detectado)
        cic_extraido = cic_match.group(1) if cic_match else (cls._CIC_FALLBACK_REGEX.search(texto_detectado).group(0) if cls._CIC_FALLBACK_REGEX.search(texto_detectado) else None)
        
        ocr_id_cr_match = cls._OCR_ID_CR_REGEX.search(texto_detectado)
        fecha_nac_match = cls._FECHA_NAC_REGEX.search(texto_detectado)
        sexo_match = cls._SEXO_REGEX.search(texto_detectado)
        vigencia_match = cls._VIGENCIA_REGEX.search(texto_detectado)

        confidencias = [d.get('Confidence') for d in detecciones if d.get('Type') == 'LINE' and d.get('Confidence')  is not None]
        promedio_confianza = round(sum(confidencias) / len(confidencias), 2) if confidencias else None
        
        fecha_nacimiento = None
        if fecha_nac_match:
            try:
                fecha_nacimiento = timezone.datetime.strptime(fecha_nac_match.group(1).replace('-', '/'), '%d/%m/%Y').date()
            except ValueError:
                pass

        return {
            'nombre_extraido': nombre,
            'apellido_paterno_extraido': apellido_paterno,
            'apellido_materno_extraido': apellido_materno,
            'curp_extraida': curp_match.group(0) if curp_match else None,
            'clave_electoral_extraida': clave_match.group(0) if clave_match else None,
            'cic_extraido': cic_extraido,
            'ocr_id_cr_extraido': ocr_id_cr_match.group(0) if ocr_id_cr_match else None,
            'fecha_nacimiento_extraida': fecha_nacimiento,
            'sexo_extraido': sexo_match.group(1) if sexo_match else None,
            'vigencia_extraida': f"{vigencia_match.group(1)}-{vigencia_match.group(2)}" if vigencia_match else None,
            'confianza_ocr': promedio_confianza,
            'respuesta_ocr_completa': {'texto_detectado': texto_detectado},
            'texto_detectado': texto_detectado,
            'tiempo_procesamiento_ms': int((time.perf_counter() - start_time) * 1000),
        }

    @classmethod
    def procesar_archivos(cls, usuario: Usuarios, archivos_a_procesar: list, id_relacionado: int = None):
        """
        Procesa archivos INES (frontales y/o traseros) usando OCR.
        Retorna un dict con el estado final: {'ok': bool, 'errores_campos': list, 'duplicados': list, 'resultados': list}
        """
        analisis = []
        errores_campos = []
        duplicados = []

        for tipo_doc_actual, archivo_actual in archivos_a_procesar:
            archivo_actual.seek(0)
            imagen_bytes = archivo_actual.read()
            try:
                datos_ocr = cls._extraer_datos_ocr(imagen_bytes)
            except Exception as exc:
                raise ValueError(f"Error al procesar OCR ({tipo_doc_actual}): {str(exc)}")

            # Validar campos vitales
            faltantes = []
            if tipo_doc_actual == 'INE_FRONTAL':
                if not datos_ocr.get('curp_extraida'): faltantes.append('curp_extraida')
                if not datos_ocr.get('clave_electoral_extraida'): faltantes.append('clave_electoral_extraida')
            elif tipo_doc_actual == 'INE_TRASERA':
                if not datos_ocr.get('cic_extraido'): faltantes.append('cic_extraido')
                if not datos_ocr.get('ocr_id_cr_extraido'): faltantes.append('ocr_id_cr_extraido')

            if faltantes:
                errores_campos.append({'tipo_documento': tipo_doc_actual, 'campos_faltantes': faltantes, 'texto': datos_ocr.get('texto_detectado')})

            # Check duplicados
            validaciones = [('curp_extraida', 'CURP'), ('cic_extraido', 'CIC'), ('ocr_id_cr_extraido', 'OCR_ID_CR'), ('clave_electoral_extraida', 'CLAVE_ELECTORAL')]
            for f_name, label in validaciones:
                val = datos_ocr.get(f_name)
                if val and DocumentosOCR.objects.filter(**{f_name: val}).exists():
                    duplicados.append({'tipo_documento': tipo_doc_actual, 'campo': label, 'valor': val})

            analisis.append({'tipo_documento': tipo_doc_actual, 'archivo': archivo_actual, 'datos_ocr': datos_ocr})

        if errores_campos or duplicados:
            return {'ok': False, 'errores_campos': errores_campos, 'duplicados': duplicados}

        estado_completado = EstadoOCR.objects.get(nombre__iexact='Completado')
        resultados = []
        doc_frontal_id, doc_trasera_id = None, None

        with transaction.atomic():
            for item in analisis:
                tipo_doc = item['tipo_documento']
                archivo = item['archivo']
                datos = item['datos_ocr']

                nombre_archivo = default_storage.save(f"ocr/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{archivo.name}", archivo)
                
                documento = DocumentosOCR.objects.create(
                    id_usuario=usuario,
                    tipo_documento=tipo_doc,
                    id_relacionado=id_relacionado,
                    ruta_imagen=nombre_archivo,
                    id_estado=estado_completado,
                    fecha_procesamiento=timezone.now(),
                    intentos_procesamiento=1,
                    **{k: v for k, v in datos.items() if hasattr(DocumentosOCR, k)}
                )

                LogOCR.objects.create(
                    id_documento_ocr=documento,
                    estado_nuevo=estado_completado,
                    mensaje='Documento validado y guardado correctamente.',
                    tiempo_procesamiento_ms=datos.get('tiempo_procesamiento_ms')
                )

                resultados.append(documento)
                if tipo_doc == 'INE_FRONTAL': doc_frontal_id = documento.id
                elif tipo_doc == 'INE_TRASERA': doc_trasera_id = documento.id

            # Update user profile
            if doc_frontal_id or doc_trasera_id:
                if doc_frontal_id: usuario.imagen_ine_frontal_url = str(doc_frontal_id)
                if doc_trasera_id: usuario.imagen_ine_trasera_url = str(doc_trasera_id)
                usuario.save()

        return {'ok': True, 'resultados': resultados}
