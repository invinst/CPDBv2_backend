from .common import DATABASES, prod_env
from .common import *  # NOQA

import environ

env = environ.Env()

DEBUG = False

CORS_ORIGIN_WHITELIST = (
    'ms.cpdp.co',
    )

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/pyenv/versions/cpdb/emails'

DATABASES['default']['HOST'] = prod_env.str('POSTGRES_STAGING_FQDN')

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

ANYMAIL = {
    'MAILGUN_API_KEY': env.str('MAILGUN_API_KEY'),
    'MAILGUN_SENDER_DOMAIN': 'cpdp.co'
}

EMAIL_BACKEND = 'anymail.backends.mailgun.MailgunBackend'
DEFAULT_FROM_EMAIL = 'info@cpdp.co'
