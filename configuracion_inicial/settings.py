"""
Django settings for configuracion_inicial project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-q99h-^75b%!)f$lx5i_r(xordl(+o4s1&y*if$2l27il+-n=ys'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    'django_filters',
    'members',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'configuracion_inicial.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'members' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'configuracion_inicial.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aquiestoy',        
        'USER': 'victxfl',           
        'PASSWORD': '',            
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Mexico_City'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'members' / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

LOGIN_URL = 'members:login'
LOGIN_REDIRECT_URL = 'members:feed'
LOGOUT_REDIRECT_URL = 'members:login'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Sistema de Gestión de Casos Sociales - API',
    'DESCRIPTION': 'API REST para gestión de casos sociales, donaciones y usuarios',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'COMPONENT_SPLIT_REQUEST': True,
    'SERVERS': [
        {'url': 'http://127.0.0.1:8000', 'description': 'Desarrollo Local'},
    ],
    'TAGS': [
        {'name': 'Autenticación', 'description': 'Endpoints de autenticación y tokens JWT'},
        {'name': 'Usuarios', 'description': 'Gestión completa de usuarios del sistema'},
        {'name': 'Tipos de Usuario', 'description': 'Catálogo de roles y tipos de usuario'},
        {'name': 'Casos', 'description': 'Gestión de casos sociales'},
        {'name': 'Estados de Caso', 'description': 'Catálogo de estados para casos'},
        {'name': 'Categorías', 'description': 'Categorías de clasificación de casos'},
        {'name': 'Caso-Categorías', 'description': 'Relación entre casos y categorías'},
        {'name': 'Donaciones', 'description': 'Gestión de donaciones y contribuciones'},
        {'name': 'Evidencias', 'description': 'Archivos multimedia de evidencia de casos'},
        {'name': 'Conversaciones', 'description': 'Hilos de conversación entre usuarios'},
        {'name': 'Mensajes', 'description': 'Mensajes dentro de conversaciones'},
        {'name': 'Tipos de Mensaje', 'description': 'Catálogo de tipos de mensaje'},
        {'name': 'Reportes', 'description': 'Reportes de usuarios o contenido inapropiado'},
        {'name': 'Estados de Reporte', 'description': 'Catálogo de estados de reportes'},
        {'name': 'Sanciones', 'description': 'Sanciones aplicadas a usuarios'},
        {'name': 'Tipos de Sanción', 'description': 'Catálogo de tipos de sanción'},
        {'name': 'Documentos OCR', 'description': 'Documentos procesados con OCR'},
        {'name': 'Estados OCR', 'description': 'Catálogo de estados de procesamiento OCR'},
        {'name': 'Log OCR', 'description': 'Historial de procesamiento OCR'},
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

AUTH_USER_MODEL = 'members.Usuarios'
