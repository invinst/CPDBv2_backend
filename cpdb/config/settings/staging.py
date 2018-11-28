from .production import *  # NOQA

import environ


env = environ.Env()

CORS_ORIGIN_WHITELIST = (
    'ms.cpdp.co',
    'staging.cpdp.co',
    'staging.cpdb.co',
)

V1_URL = 'https://staging.cpdb.co'
DOMAIN = 'https://staging.cpdp.co'
AZURE_STATICFILES_SSL = True

TWITTERBOT_ENV = 'dev'

AIRTABLE_COPA_AGENCY_ID = 'recMBxxV8FCMqri2O'
AIRTABLE_CPD_AGENCY_ID = 'rec6zglKh8mWa4Ycg'

ENVIRONMENT = 'staging'
