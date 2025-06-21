"""
PRODUCTION SETTINGS
Django settings for progress_rpg project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from .base import *

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
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },

    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "errors": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

DEBUG = os.environ.get('DEBUG')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')

print("DEBUG:", DEBUG)

REGISTRATION_ENABLED = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'app.progressrpg.com').split(',')
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'https://app.progressrpg.com/').split(',')
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://app.progressrpg.com/').split(',')

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=60, ssl_require=True)
}


REDIS_URL = os.environ.get('REDIS_URL')
#print("REDIS_HOST:", REDIS_HOST)

ssl_required = os.environ.get("REDIS_VERIFY_SSL", "true").lower() == "true"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": 'channels_redis.core.RedisChannelLayer',
        "CONFIG": {
            "hosts": [{
                "address": REDIS_URL,
                "ssl_cert_reqs": ssl.CERT_REQUIRED  if ssl_required else ssl.CERT_NONE,
                
            }],
        },
    },
}

CACHES = {
    'default': {
        "BACKEND": 'django_redis.cache.RedisCache',
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'ssl_cert_reqs': ssl.CERT_REQUIRED  if ssl_required else ssl.CERT_NONE,
        }
    }
}

CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
CELERY_BROKER_URL = os.environ.get('REDIS_URL')


# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = 'default'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False

SESSION_COOKIE_NAME = 'sessionid'
#SESSION_COOKIE_DOMAIN = '.progressrpg.com'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_DOMAIN = '.progressrpg.com'

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = []
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'