from .common import *  # NOQA

DEBUG = False


INSTALLED_APPS += ('corsheaders',)
MIDDLEWARE_CLASSES += (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware')

CORS_ORIGIN_WHITELIST = (
    'ms.cpdp.co',
    )
