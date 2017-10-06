import shutil
import os

from nose.plugins.base import Plugin

from snapshot_test.mixins import SnapshotTestMixin


class CreateSnapshotPlugin(Plugin):
    """Create/update snapshots instead of testing them."""

    name = 'create-snapshot'
    score = 101
    enableOpt = 'create_snapshot'
    clobber = False

    def options(self, parser, env):
        parser.add_option(
            '--create-snapshot', dest=self.enableOpt, action='store_true',
            help='Create/update snapshots instead of testing them.')
        parser.add_option(
            '--snapshot-clobber', dest='snapshot_clobber', action='store_true',
            help='Overwrite previously stored snapshot.')

    def configure(self, options, config):
        self.enabled = getattr(options, self.enableOpt, False)
        self.clobber = options.snapshot_clobber

    def wantClass(self, cls):
        return issubclass(cls, SnapshotTestMixin)

    def wantFunction(self, func):
        return False

    def prepareTestCase(self, test):
        test.test.enable_create_snapshot_mode()
        test.test.set_clobber(self.clobber)


class CleanupDirIfSuccessPlugin(Plugin):
    name = 'cleanup dir if success'
    score = 100
    enabled = True

    def __init__(self, *args, **kwargs):
        self.dirs = set()

    def options(self, parser, env):
        pass

    def configure(self, options, config):
        pass

    def prepareTestCase(self, test):
        try:
            self.dirs = self.dirs | set(test.test.cleanupdirs)
        except AttributeError:
            pass

    def finalize(self, result):
        if result.wasSuccessful():
            for dir in self.dirs:
                if os.path.isdir(dir):
                    shutil.rmtree(dir)
