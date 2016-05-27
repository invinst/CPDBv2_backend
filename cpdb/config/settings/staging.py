from .common import *  # NOQA

INSTALLED_APPS += ('corsheaders',)
MIDDLEWARE_CLASSES += (
    'corsheaders.middleware.CorsMiddleware',
)
CORS_ORIGIN_WHITELIST = (
    '23.96.180.229:8888',
    )

DEBUG = False
