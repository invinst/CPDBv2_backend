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
