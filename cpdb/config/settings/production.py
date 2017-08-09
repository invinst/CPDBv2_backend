from .common import *  # NOQA

import environ

env = environ.Env()

DEBUG = False


INSTALLED_APPS += ('corsheaders',)  # NOQA
MIDDLEWARE_CLASSES += (  # NOQA
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware')

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
