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
