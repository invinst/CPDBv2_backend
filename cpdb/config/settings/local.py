from .common import *  # NOQA


INSTALLED_APPS += ('corsheaders', 'django_extensions')  # NOQA
MIDDLEWARE_CLASSES += (  # NOQA
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',)

CORS_ORIGIN_WHITELIST = (
    'localhost:9966',
    )

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

MEDIA_ROOT = '/www/media/'

DEBUG = True
