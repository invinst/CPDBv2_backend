from .common import *  # NOQA
from .common import APPS_DIR


TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
MEDIA_ROOT = str(APPS_DIR('test_media'))
TEST = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {},
    'handlers': {},
    'loggers': {}
}


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

DOMAIN = 'http://foo.com'

TWITTERBOT_ENV = 'test'

V1_URL = 'http://cpdb.lvh.me'
