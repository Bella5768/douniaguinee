"""
Django settings for dounia_project project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dounia-dev-key-change-in-production-2024!')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [h.strip() for h in os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    'localhost,127.0.0.1'
).split(',') if h.strip()]

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'http://127.0.0.1:8000,http://localhost:8000'
).split(',') if o.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inscriptions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE.insert(3, 'dounia_project.middleware.TrustLocalhostCSRFMiddleware')

ROOT_URLCONF = 'dounia_project.urls'

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
                'inscriptions.context_processors.site_configuration',
            ],
        },
    },
]

WSGI_APPLICATION = 'dounia_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'False').lower() in ('true', '1', 'yes')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Email configuration — SMTP par défaut
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True

# Gmail SMTP
GMAIL_HOST = 'smtp.gmail.com'
GMAIL_PORT = 587
GMAIL_USER = os.environ.get('GMAIL_USER', '')
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD', '')

# Outlook SMTP
OUTLOOK_HOST = 'smtp.office365.com'
OUTLOOK_PORT = 587
OUTLOOK_USER = os.environ.get('OUTLOOK_USER', '')
OUTLOOK_PASSWORD = os.environ.get('OUTLOOK_PASSWORD', '')

# Serveur par défaut (gmail ou outlook)
DEFAULT_EMAIL_PROVIDER = os.environ.get('DEFAULT_EMAIL_PROVIDER', 'gmail')

if DEFAULT_EMAIL_PROVIDER == 'outlook':
    EMAIL_HOST = OUTLOOK_HOST
    EMAIL_PORT = OUTLOOK_PORT
    EMAIL_HOST_USER = OUTLOOK_USER
    EMAIL_HOST_PASSWORD = OUTLOOK_PASSWORD
    DEFAULT_FROM_EMAIL = OUTLOOK_USER
else:
    EMAIL_HOST = GMAIL_HOST
    EMAIL_PORT = GMAIL_PORT
    EMAIL_HOST_USER = GMAIL_USER
    EMAIL_HOST_PASSWORD = GMAIL_PASSWORD
    DEFAULT_FROM_EMAIL = GMAIL_USER
