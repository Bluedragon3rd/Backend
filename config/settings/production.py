from .base import *

# docker compose -f docker-compose.prod.yml up -d --build
# docker compose -f docker-compose.prod.yml down
# docker compose -f docker-compose.prod.yml up -d
# docker logs -f {name}
DEBUG = False
ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://my-frontend-domain.com",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}