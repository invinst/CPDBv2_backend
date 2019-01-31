from .production import *  # NOQA

import environ


env = environ.Env()

CORS_ORIGIN_WHITELIST = (
    'ms.cpdp.co',
    'staging.cpdp.co',
    'staging.cpdb.co',
    'test-social-graph.herokuapp.com'
)

V1_URL = 'https://staging.cpdb.co'
DOMAIN = 'https://staging.cpdp.co'
AZURE_STATICFILES_SSL = True

TWITTERBOT_ENV = 'dev'

AIRTABLE_COPA_AGENCY_ID = 'recMBxxV8FCMqri2O'
AIRTABLE_CPD_AGENCY_ID = 'rec6zglKh8mWa4Ycg'

ENVIRONMENT = 'staging'

EMAIL_BACKEND = 'email_service.backend.MailGunHijackBackend'
BANDIT_EMAIL = ['cpdb.dev+hijack@eastagile.com', 'cpdp+notifications@invisibleinstitute.com']

S3_BUCKET_OFFICER_CONTENT = 'officer-content-staging'
LAMBDA_FUNCTION_CREATE_OFFICER_ZIP_FILE = 'createOfficerZipFileStaging'
LAMBDA_FUNCTION_UPLOAD_PDF = 'uploadPdfStaging'
