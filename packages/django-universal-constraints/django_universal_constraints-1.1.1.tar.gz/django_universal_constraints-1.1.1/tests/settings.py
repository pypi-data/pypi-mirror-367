"""
Django settings for testing django-universal-constraints.
"""

import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'test-secret-key-for-django-universal-constraints'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'universal_constraints',
    'tests',
]

# Ensure test models are created
DATABASE_ROUTERS = []

MIDDLEWARE = []

TEMPLATES = []

WSGI_APPLICATION = None

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'test': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Universal constraints configuration for testing
UNIVERSAL_CONSTRAINTS = {
    'test': {
        'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
        'RACE_CONDITION_PROTECTION': True,
        'LOG_LEVEL': 'DEBUG',
    },
    'default': {
        'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
        'RACE_CONDITION_PROTECTION': True,
        'LOG_LEVEL': 'DEBUG',
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'universal_constraints': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
