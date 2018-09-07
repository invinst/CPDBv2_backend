from .production import *  # NOQA

import environ

env = environ.Env()

CORS_ORIGIN_WHITELIST = (
    'ms.cpdp.co',
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
            'filename': '/pyenv/versions/cpdb/logs/django-error.log',
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

V1_URL = 'http://staging.cpdb.co'
DOMAIN = 'http://staging.cpdp.co'
AZURE_STATICFILES_SSL = False

TWITTERBOT_ENV = 'dev'
