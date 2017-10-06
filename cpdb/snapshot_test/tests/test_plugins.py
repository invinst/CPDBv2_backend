from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from snapshot_test.plugins import CreateSnapshotPlugin, CleanupDirIfSuccessPlugin
from snapshot_test.mixins import SnapshotTestMixin


class CreateSnapshotPluginTestCase(SimpleTestCase):
    def test_options(self):
        env = Mock()
        parser = Mock()
        plugin = CreateSnapshotPlugin()
        plugin.options(parser, env)
        expect(parser.add_option).to.be.any_call(
            '--create-snapshot', dest='create_snapshot', action='store_true',
            help='Create/update snapshots instead of testing them.')
        expect(parser.add_option).to.be.any_call(
            '--snapshot-clobber', dest='snapshot_clobber', action='store_true',
            help='Overwrite previously stored snapshot.')

    def test_configure(self):
        config = Mock()
        options = Mock()
        plugin = CreateSnapshotPlugin()
        plugin.configure(options, config)
        expect(plugin.enabled).to.equal(options.create_snapshot)
        expect(plugin.clobber).to.equal(options.snapshot_clobber)

    def test_wantCLass(self):
        class TestA(SnapshotTestMixin):
            pass

        class TestB:
            pass

        plugin = CreateSnapshotPlugin()
        expect(plugin.wantClass(TestA)).to.be.true()
        expect(plugin.wantClass(TestB)).to.be.false()

    def test_wantFunction(self):
        plugin = CreateSnapshotPlugin()
        expect(plugin.wantFunction(Mock())).to.be.false()

    def test_prepareTestCase(self):
        test = Mock(test=Mock())
        plugin = CreateSnapshotPlugin()
        plugin.clobber = True
        plugin.prepareTestCase(test)
        expect(test.test.enable_create_snapshot_mode).to.be.called_once()
        expect(test.test.set_clobber).to.be.called_once_with(True)


class CleanupDirIfSuccessPluginTestCase(SimpleTestCase):
    def setUp(self):
        self.plugin = CleanupDirIfSuccessPlugin()

    def test_PrepareTestCase(self):
        test_1 = Mock(test=Mock(cleanupdirs=['abc']))
        test_2 = Mock(test='some string')

        self.plugin.prepareTestCase(test_1)
        expect(self.plugin.dirs).to.eq(set(['abc']))

        self.plugin.prepareTestCase(test_2)
        expect(self.plugin.dirs).to.eq(set(['abc']))

    @patch('cpdb.snapshot_test.plugins.os.path.isdir')
    @patch('cpdb.snapshot_test.plugins.shutil.rmtree')
    def test_finalize(self, mock_rmtree, mock_isdir):
        result = Mock(wasSuccessful=Mock(return_value=True))
        self.plugin.dirs = set(['abc'])

        mock_isdir.return_value = True
        self.plugin.finalize(result)
        expect(mock_rmtree).to.be.called_once_with('abc')

        mock_rmtree.reset_mock()
        mock_isdir.return_value = False
        self.plugin.finalize(result)
        expect(mock_rmtree).not_to.be.called()
