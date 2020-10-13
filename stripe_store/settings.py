import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '7@4rn4uss&kp$ir1vj%&fg@ch@#3z6v&mlaf4urk&(nwmtqko2'

STRIPE_PUBLISHABLE_KEY = 'pk_test_51HahZwJe5a5futjdSQ9NWxDjphOykmzESUIfiIuLleBEJ90kJhOzq0FJucrHnPHj1bX0CuBg1UXtgmijVCAFRGeg001AtWhhFl'

STRIPE_SECRET_KEY = 'sk_test_51HahZwJe5a5futjdcJNZqkLM335XzDJy2CrwC25ANhnXXApkXJa2lkKtetc7rJb3VWWdX3gAC2kuALIVLQ8tjgyU00FKJ9805s'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'store.apps.StoreConfig',
    'silk',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'silk.middleware.SilkyMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stripe_store.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'stripe_store.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.postgresql_psycopg2',   # "django.db.backends.sqlite3"
        "NAME": 'stripe_store',
        "USER": 'stripe_store_admin',
        "PASSWORD": 'stripe_store_admin',
        "HOST": 'db',
        "PORT": '5432',
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
