from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'my_database',
        'USER': 'root',
        'PASSWORD': '1234',
        'HOST': 'db',
        'PORT': '3306',
    }
}