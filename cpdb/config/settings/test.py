from .common import *  # NOQA
from .common import INSTALLED_APPS


TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
MEDIA_ROOT = str(APPS_DIR('test_media'))  # NOQA
TEST = True

INSTALLED_APPS += ('pinboard.tests',)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {},
    'handlers': {},
    'loggers': {}
}

DOMAIN = 'http://foo.com'

TWITTERBOT_ENV = 'test'

V1_URL = 'http://cpdb.lvh.me'

ENABLE_SITEMAP = True


# OVERRIDE PROTECTED KEYS from common
MAILCHIMP_API_KEY = ''
MAILCHIMP_USER = ''
AZURE_STORAGE_ACCOUNT_NAME = ''
AZURE_STORAGE_ACCOUNT_KEY = ''
TWITTERBOT_STORAGE_ACCOUNT_NAME = ''
TWITTERBOT_STORAGE_ACCOUNT_KEY = ''
DATA_PIPELINE_STORAGE_ACCOUNT_NAME = ''
DATA_PIPELINE_STORAGE_ACCOUNT_KEY = ''
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_APP_TOKEN_KEY = ''
TWITTER_APP_TOKEN_SECRET = ''
DOCUMENTCLOUD_USER = 'DOCUMENTCLOUD_USER'
DOCUMENTCLOUD_PASSWORD = 'DOCUMENTCLOUD_PASSWORD'
GOOGLE_GEOCODE_APIKEY = ''
AIRTABLE_PROJECT_KEY = ''
AIRTABLE_TABLE_NAME = ''
GOOGLE_APPLICATION_CREDENTIALS = ''
CPDP_ALERTS_WEBHOOK = 'CPDP_ALERTS_WEBHOOK'
ENABLE_MAKE_CLOUD_DOCUMENTS_PUBLIC = True

GA_TRACKING_ID = 'GA_TRACKING_ID'
CLICKY_TRACKING_ID = 'CLICKY_TRACKING_ID'
CLICKY_SITEKEY_ADMIN = 'CLICKY_SITEKEY_ADMIN'

AIRTABLE_LAWSUITS_PROJECT_KEY = 'AIRTABLE_LAWSUITS_PROJECT_KEY'
