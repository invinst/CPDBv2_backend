from .common import *  # NOQA


INSTALLED_APPS += (  # NOQA
    'django_extensions',
    'debug_toolbar',
)

CORS_ORIGIN_WHITELIST = (
    'localhost:9966',
    'localhost:9967',
    'localhost:8001',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

MEDIA_ROOT = '/www/media/'
DOMAIN = 'http://localhost:9966'
V1_URL = 'http://localhost:8001'

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
}
RUNNING_PORT = '8000'

NOTEBOOK_ARGUMENTS = [
    '--ip=0.0.0.0',
    '--port=8888',
    '--no-browser',
]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # NOQA
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += ('shared.browsable_api_renderder_without_form.BrowsableAPIRendererWithoutForms',)  # NOQA
INTERNAL_IPS = ['10.0.2.2']
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}

TWITTERBOT_ENV = 'dev'

S3_BUCKET_OFFICER_CONTENT = 'officer-content-staging'
S3_BUCKET_CRAWLER_LOG = 'cpdp-crawler-logs-develop'
LAMBDA_FUNCTION_CREATE_OFFICER_ZIP_FILE = 'createOfficerZipFileStaging'
LAMBDA_FUNCTION_UPLOAD_PDF = 'uploadPdfStaging'
