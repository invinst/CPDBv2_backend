from .production import *  # NOQA

import environ


env = environ.Env()

CORS_ORIGIN_WHITELIST = (
    'ms.cpdp.co',
    'staging.cpdp.co',
    'staging.cpdb.co',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'error-file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/logfiles/django-error.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['error-file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

V1_URL = 'https://staging.cpdb.co'
DOMAIN = 'https://staging.cpdp.co'
AZURE_STATICFILES_SSL = True

TWITTERBOT_ENV = 'dev'

AIRTABLE_COPA_AGENCY_ID = 'recMBxxV8FCMqri2O'
AIRTABLE_CPD_AGENCY_ID = 'rec6zglKh8mWa4Ycg'
