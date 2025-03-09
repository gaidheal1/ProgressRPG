"""
Django settings for progress_rpg project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import dj_database_url
from decouple import Config, RepositoryEnv, config
import os
from dotenv import load_dotenv
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters' : {
        'verbose': {
            "format": "[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[%(levelname)s] %(message)s",
        },
    },

    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file_general": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/general.log"),
            "formatter": "verbose",
            "maxBytes": 5*1024*1024, # 5MB per file
            "backupCount": 3, # Keep last 3 log files
        },
        "file_errors": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/errors.log"),
            "formatter": "verbose",
            "maxBytes": 5*1024*1024, # 5MB per file
            "backupCount": 3, # Keep last 3 log files
        },
        "file_activity": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/activity.log"),
            "formatter": "verbose",
            "maxBytes": 5*1024*1024, # 5MB per file
            "backupCount": 6, # Keep last 5 log files
        },
    },

    "loggers": {
        "django": {
            "handlers": ["console", "file_general"],
            "level": "INFO",
            "propagate": True,
        },
        "errors": {
            "handlers": ["file_errors"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

REGISTRATION_ENABLED = True
SECRET_KEY_FALLBACKS=['django-insecure-46)84p=e^!*as-px9&4pl0jqh7wfy$clbwtu3(%9$qj&(5ri-$']

ON_HEROKU = "DYNO" in os.environ

if ON_HEROKU:
    DEBUG = os.environ.get('DEBUG')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')

    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = os.environ.get('EMAIL_PORT')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')

else:
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    DB_NAME = os.getenv('DB_NAME', default='progress_rpg')
    DB_USER = os.getenv('DB_USERNAME', default='duncan')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    DB_HOST = os.getenv('DB_HOST', default='localhost')
    DB_PORT = os.getenv('DB_PORT', default=5432)

    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = os.getenv('EMAIL_PORT')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')

print("DEBUG:", DEBUG)




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if ON_HEROKU:
    SECRET_KEY = os.environ.get('SECRET_KEY')
else:
    SECRET_KEY = os.getenv('SECRET_KEY')



if ON_HEROKU:
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1').split(',')
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '127.0.0.1:8000').split(',')
else:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1').replace('\r', '').split(',')
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://127.0.0.1,http://localhost:8000').split(',')

#print("ALLOWED HOSTS:", ALLOWED_HOSTS)
#print("CORS:", CORS_ALLOWED_ORIGINS)

CSRF_TRUSTED_ORIGINS = [
    'https://progress-rpg-dev-6581f3bc144e.herokuapp.com/',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://localhost:5173',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'rest_framework',
    'channels',
    #'django-vite',
    'character',
    'users',
    'gameplay',
    'gameworld',
    'events',
    'locations',
    'payments',

    'decouple',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'progress_rpg.urls'

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

#WSGI_APPLICATION = 'progress_rpg.wsgi.application'
ASGI_APPLICATION = "progress_rpg.asgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

if ON_HEROKU:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }

if ON_HEROKU:
    REDIS_HOST = (os.environ.get('REDIS_URL'))
else:
    REDIS_HOST = ('redis://localhost:6379')


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": 'channels_redis.core.RedisChannelLayer',
        "CONFIG": {
            "hosts": [REDIS_HOST],   
        },
    },
}


CACHES = {
    'default': {
        "BACKEND": 'django.core.cache.backends.redis.RedisCache',
        "LOCATION": REDIS_HOST,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }

    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'users.CustomUser'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [Path(BASE_DIR / 'static')]
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email settings (host, port and password are at top)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'admin@progressrpg.com'
DEFAULT_FROM_EMAIL = 'admin@progressrpg.com'

# Optionally, configure for error emails
ADMINS = [('Admin', 'admin@progressrpg.com')]  # The emails to receive error notifications

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 3600  # 1 hour in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True

if ON_HEROKU:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# For local development only
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_DOMAIN = None
    CSRF_COOKIE_SECURE = False
    SECURE_PROXY_SSL_HEADER = None
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False


LOGIN_REDIRECT_URL = '/'  # Or wherever you want to go after login
LOGIN_URL = '/login/'  # Customize the login URL


STRIPE_PUBLIC_KEY = "pk_test_51QNRgsGHaENuGVuPh70KmxNTGK3iQPJgjGO2gVcdE0dlRDG7LOZfY3zQxvEdR2hmXDKaEILIRKEnJdn69arGwKCi00bSZWzrzW"
STRIPE_SECRET_KEY = "nope"

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
if ON_HEROKU:
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
else:
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

