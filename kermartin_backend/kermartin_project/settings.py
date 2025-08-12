"""
Django settings for Kermartin 3.0 project.
Sistema de análise jurídica especializado em Tribunal do Júri
"""

import os
from pathlib import Path
from decouple import AutoConfig
try:
    import dj_database_url  # type: ignore
except Exception:  # pragma: no cover - optional in dev/test
    dj_database_url = None  # type: ignore

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carregar .env a partir da raiz do repositório (BASE_DIR.parent)
config = AutoConfig(search_path=BASE_DIR.parent)
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='kermartin-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
]

LOCAL_APPS = [
    'kermartin_backend.core',
    'kermartin_backend.ai_engine',
    'kermartin_backend.authentication',
    'kermartin_backend.webui',
    'kermartin_backend.juris',
]


INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'kermartin_backend.core.middleware.SecurityMiddleware',
    'kermartin_backend.core.middleware.RateLimitMiddleware',
    'kermartin_backend.core.middleware.PerformanceMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'kermartin_backend.core.middleware.CORSMiddleware',
]

ROOT_URLCONF = 'kermartin_backend.kermartin_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'kermartin_backend.kermartin_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'kermartin_dev.sqlite3',
    }
}

# Use DATABASE_URL if provided (Render/Postgres)
DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL and dj_database_url:
    DATABASES['default'] = dj_database_url.config(  # type: ignore[attr-defined]
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Kermartin 3.0 API',
    'DESCRIPTION': 'APIs de análise jurídica do Kermartin 3.0',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# OpenAI Configuration
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4-1106-preview')
OPENAI_MAX_TOKENS = config('OPENAI_MAX_TOKENS', default=4000, cast=int)

# Redis Configuration
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'kermartin.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'kermartin': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'ai_engine': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Criar diretório de logs
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Configurações específicas para produção
if not DEBUG:
    # Whitenoise para servir arquivos estáticos
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # Cache com Redis em produção
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

    # Configurações de segurança para produção
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Kermartin Specific Settings
KERMARTIN_SETTINGS = {
    'MAX_DOCUMENT_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_FILE_TYPES': ['pdf'],
    'ANALYSIS_TIMEOUT': 300,  # 5 minutes
    'CACHE_ANALYSIS_RESULTS': True,
    'CACHE_TIMEOUT': 3600,  # 1 hour
    'SECURITY_MAX_CONTENT_LENGTH': int(os.getenv('SECURITY_MAX_CONTENT_LENGTH', 300000)),  # chars
    'CHUNK_SIZE_CHARS': int(os.getenv('CHUNK_SIZE_CHARS', 12000)),
    'CHUNK_OVERLAP_CHARS': int(os.getenv('CHUNK_OVERLAP_CHARS', 800)),
    'OPENAI_RETRY_MAX_ATTEMPTS': int(os.getenv('OPENAI_RETRY_MAX_ATTEMPTS', 6)),
    'OPENAI_RETRY_BASE_DELAY_SEC': float(os.getenv('OPENAI_RETRY_BASE_DELAY_SEC', 1.5)),
    'OPENAI_CHUNK_SLEEP_SEC': float(os.getenv('OPENAI_CHUNK_SLEEP_SEC', 0.25)),
}

# Rate limiting strategy
# Preferir middleware centralizado; desabilita verificação em SecurityValidator
USE_SECURITY_VALIDATOR_RATE_LIMIT = False

# Jurisprudence / GraphRAG toggles
JURIS_GRAPH_ENABLED = config('JURIS_GRAPH_ENABLED', default=False, cast=bool)
JURIS_RETRIEVAL_PROVIDER = config('JURIS_RETRIEVAL_PROVIDER', default='simple')
JURIS_GRAPH_URL = config('JURIS_GRAPH_URL', default='bolt://localhost:7687')
JURIS_GRAPH_USER = config('JURIS_GRAPH_USER', default='neo4j')
JURIS_GRAPH_PASSWORD = config('JURIS_GRAPH_PASSWORD', default='')
JURIS_GRAPH_TIMEOUT_MS = config('JURIS_GRAPH_TIMEOUT_MS', default=2000, cast=int)
JURIS_RAG_VECTOR_STORE = config('JURIS_RAG_VECTOR_STORE', default='pgvector')
JURIS_RAG_TOPK = config('JURIS_RAG_TOPK', default=8, cast=int)
