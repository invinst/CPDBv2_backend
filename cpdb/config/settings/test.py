from .common import *  # NOQA
from .common import APPS_DIR, INSTALLED_APPS


TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
MEDIA_ROOT = str(APPS_DIR('test_media'))
TEST = True

NOSE_PLUGINS = [
    'snapshot_test.plugins.CreateSnapshotPlugin',
    'snapshot_test.plugins.CleanupDirIfSuccessPlugin'
]

INSTALLED_APPS += ('snapshot_test',)
