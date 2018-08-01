from .common import prod_env
from .common import *  # NOQA

import environ

env = environ.Env()

DEBUG = False

CORS_ORIGIN_WHITELIST = (
    'mb.cpdp.co',
    )

ANYMAIL = {
    'MAILGUN_API_KEY': env.str('MAILGUN_API_KEY'),
    'MAILGUN_SENDER_DOMAIN': 'cpdp.co'
}

EMAIL_BACKEND = 'anymail.backends.mailgun.MailgunBackend'
DEFAULT_FROM_EMAIL = 'info@cpdp.co'
DOMAIN = 'https://beta.cpdp.co'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': prod_env.str('APP_DB'),
        'USER': prod_env.str('APP_LOGIN'),
        'PASSWORD': prod_env.str('APP_PASSWORD'),
        'HOST': prod_env.str('POSTGRES_PRODUCTION_FQDN'),
        'PORT': '5432',
        'ATOMIC_REQUESTS': True
    }
}
