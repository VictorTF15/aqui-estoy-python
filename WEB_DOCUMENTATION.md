# Documentación Técnica SOA: Aquí Estoy API

## 1. Paradigma de Servicios (SOA) y su Importancia
El patrón arquitectónico implementado (Service Layer) separa de manera estricta la **Presentación y Recepción HTTP (Views/Endpoints)** de la **Lógica de Negocios (Services)** y la **Lógica de Consulta (Selectors)**.
### Beneficios:
- **Modularidad:** El código es más fácil de mantener e identificar.
- **Pruebas:** Los servicios (ej. `DocumentoOCRService`) pueden testearse de forma independiente sin mockear toda una petición HTTP.
- **Escalabilidad:** Permite crecer o cambiar el frontend o el ORM sin tocar la lógica dura.

## 2. Estructura del Proyecto
- `configuracion_inicial/`: Settings generales, URLs principales.
- `members/`: App principal que contiene:
  - `models.py`: Modelos de la Base de Datos.
  - `api_views.py`: Endpoints REST (Controladores).
  - `services.py`: Lógica de negocio dura (Ej. Procesamiento de OCR con AWS).
  - `selectors.py`: Consultas avanzadas a la BD (Ej. Datos transformados para mapas).
  - `serializers.py`: Transformación de datos y validaciones de API.
  - `urls.py`: Enrutador de Endpoints (DRF Router).

## 3. Endpoints Principales

### Autenticación
- `POST /api/auth/login/`: Inicia sesión, devuelve JWT `access` y `refresh` token.
- `POST /api/auth/refresh/`: Refresca un token JWT expirado.

### Usuarios
- `GET /api/usuarios/`: (Admin) Lista todos los usuarios.
- `POST /api/usuarios/`: Registro de un usuario nuevo público.
- `GET /api/usuarios/me/`: Devuelve la información del usuario en sesión.
- `POST /api/usuarios/{id}/cambiar_password/`: Llama a `UsuarioService` para actualizar la contraseña.

### Casos Sociales
- `GET /api/casos/`: Paginado, filtrado y búsqueda de casos.
- `POST /api/casos/`: Crea un nuevo caso (Requiere Autenticación).
- `GET /api/casos/mapa/`: Devuelve lat/lng de los casos abiertos usando `CasoSelector`.
- `GET /api/casos/estadisticas/`: Devuelve KPIs usando `CasoSelector`.

### Donaciones
- `GET /api/donaciones/`: Listar todo.
- `GET /api/donaciones/mis_donaciones/`: Devuelve el historial de un usuario usando `DonacionSelector`.

### Generación y Procesamiento de Documentos (OCR)
- `POST /api/documentos-ocr/subir-y-procesar/`: Endpoint clave. Invoca a `DocumentoOCRService`, el cual llama a AWS Rekognition, extrae CURP, OCR_ID_CR, CIC, Fecha de Nac., vigencia y valida duplicados de la BD en un ambiente transaccional.

## 4. Uso de Programación Orientada a Objetos (POO)
- **Encapsulamiento:** Ocultamiento de la complejidad de la lógica de negocio (AWS boto3, Regex engines) dentro de clases con métodos estáticos/clase (`@classmethod`).
- **Modularidad:** Responsabilidad única (`Single Responsibility Principle`). La vista recibe la petición, el servicio valida/procesa, el selector consulta y el serializer expone los datos al cliente.
