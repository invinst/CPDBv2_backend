from .production import *  # NOQA

import environ


env = environ.Env()

CORS_ORIGIN_WHITELIST = (
    'mb.cpdp.co',
    'beta.cpdp.co',
    'staging.cpdb.co',
    'test-social-graph.herokuapp.com'
)

V1_URL = 'https://staging.cpdb.co'
DOMAIN = 'https://beta.cpdp.co'
AZURE_STATICFILES_SSL = True

TWITTERBOT_ENV = 'dev'

ENVIRONMENT = 'beta'

S3_BUCKET_OFFICER_CONTENT = 'officer-content-beta'
S3_BUCKET_CRAWLER_LOG = 'cpdp-crawler-logs-beta'
LAMBDA_FUNCTION_CREATE_OFFICER_ZIP_FILE = 'createOfficerZipFileBeta'
LAMBDA_FUNCTION_UPLOAD_PDF = 'uploadPdfBeta'
