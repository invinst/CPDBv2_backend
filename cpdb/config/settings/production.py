from .common import *  # NOQA


import environ

env = environ.Env()

DEBUG = False

CORS_ORIGIN_WHITELIST = (
    'm.cpdp.co',
    'cpdp.co',
    'beta.cpdb.co',
)

ANYMAIL = {
    'MAILGUN_API_KEY': env.str('MAILGUN_API_KEY'),
    'MAILGUN_SENDER_DOMAIN': 'cpdp.co'
}

EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
DEFAULT_FROM_EMAIL = 'info@cpdp.co'
DOMAIN = 'https://beta.cpdp.co'

STATICFILES_STORAGE = 'config.storages.AzureStorage'
AZURE_STATICFILES_CONTAINER = 'static'
AZURE_STATICFILES_SSL = True

TWITTERBOT_ENV = 'prod'

AIRTABLE_COPA_AGENCY_ID = 'rec1ue6wbuNiBYR5p'
AIRTABLE_CPD_AGENCY_ID = 'rectsNdkdCupVByTf'
