from .common import *  # NOQA


INSTALLED_APPS += ('corsheaders',)
MIDDLEWARE_CLASSES += (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware')

CORS_ORIGIN_WHITELIST = (
    'localhost:9966',
    )

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

MEDIA_ROOT = '/www/media/'

DEBUG = True
