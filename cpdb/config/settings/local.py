from .common import *  # NOQA


INSTALLED_APPS += ('django_extensions',)  # NOQA

CORS_ORIGIN_WHITELIST = (
    'localhost:9966',
    'localhost:9967',
    )

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

MEDIA_ROOT = '/www/media/'

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER = '/CPDB/CPDBv2_backend/generated_images'

RUNNING_PORT = '8000'
