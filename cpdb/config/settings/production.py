from .common import *  # NOQA


import environ
import ssl

env = environ.Env()

DEBUG = False

CORS_ORIGIN_WHITELIST = (
    'm.cpdp.co',
    'cpdp.co',
    'beta.cpdb.co',
)

ANYMAIL = {
    'MAILGUN_API_KEY': env.str('MAILGUN_API_KEY', ''),
    'MAILGUN_SENDER_DOMAIN': 'cpdp.co'
}

EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
DEFAULT_FROM_EMAIL = 'info@cpdp.co'

V1_URL = 'https://data.cpdp.co'
DOMAIN = 'https://cpdp.co'

STATICFILES_STORAGE = 'config.storages.AzureStorage'
AZURE_STATICFILES_CONTAINER = 'static'
AZURE_STATICFILES_SSL = True

TWITTERBOT_ENV = 'prod'

AIRTABLE_COPA_AGENCY_ID = 'rec1ue6wbuNiBYR5p'
AIRTABLE_CPD_AGENCY_ID = 'rectsNdkdCupVByTf'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

ENVIRONMENT = 'production'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        # 'syslog_formatter': {
        #     'format': '%(asctime)s %(environment)s [%(levelname)s] %(name)s: %(message)s',
        #     'datefmt': '%Y-%m-%dT%H:%M:%S'
        # }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'context': {
            '()': 'config.logging_filters.ContextFilter'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'syslog': {
            'level': 'INFO',
            'class': 'tlssyslog.TLSSysLogHandler',
            'formatter': 'simple',
            'address': (env.str('PAPERTRAIL_ENDPOINT'), env.int('PAPERTRAIL_PORT')),
            # 'filters': ['context'],
            'ssl_kwargs': {
                'cert_reqs': ssl.CERT_REQUIRED,
                'ssl_version': ssl.PROTOCOL_TLS,
                'ca_certs': env.str('PAPERTRAIL_CA_FILE'),
            },
        }
    },
    'loggers': {
        'django.command': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django':  {
            'handlers': ['syslog'],
            'level': 'INFO'
        }
    },
}
