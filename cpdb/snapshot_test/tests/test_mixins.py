import os
import shutil
from tempfile import NamedTemporaryFile

from django.test import SimpleTestCase

from robber import expect
from mock import Mock, patch

from snapshot_test.mixins import SnapshotTestMixin


class SnapshotTestMixinTestCase(SimpleTestCase):
    def setUp(self):
        self.mixin = SnapshotTestMixin()
        self.mixin.assertEqual = Mock()

    def test_assert_snapshot_match_with_creating_snapshot(self):
        self.mixin._create_snapshot = Mock()
        self.mixin._assert_snapshot_match = Mock()
        self.mixin.full_snapshot_path = lambda x: x
        self.mixin._is_creating_snapshot = True

        self.mixin.assert_snapshot_match('some_file_path', 'some_snapshot_path')
        expect(self.mixin._create_snapshot).to.be.called_once_with('some_file_path', 'some_snapshot_path')
        expect(self.mixin._assert_snapshot_match).not_to.be.called()

    def test_assert_snapshot_match_without_creating_snapshot(self):
        self.mixin._create_snapshot = Mock()
        self.mixin._assert_snapshot_match = Mock()
        self.mixin.full_snapshot_path = lambda x: x
        self.mixin._is_creating_snapshot = False

        self.mixin.assert_snapshot_match('some_file_path', 'some_snapshot_path')
        expect(self.mixin._assert_snapshot_match).to.be.called_once_with('some_file_path', 'some_snapshot_path')
        expect(self.mixin._create_snapshot).not_to.be.called()

    @patch('snapshot_test.mixins._app_paths', ['/myapp'])
    @patch('snapshot_test.mixins.inspect.getfile', return_value='/myapp/file')
    def test_full_snapshot_path(self, getfile):
        expect(self.mixin.full_snapshot_path('abc')).to.eq('/myapp/test_snapshots/abc')

    def test_enable_create_snapshot_mode(self):
        self.mixin.enable_create_snapshot_mode()
        expect(self.mixin._is_creating_snapshot).to.be.true()

    def test_set_clobber(self):
        self.mixin.set_clobber(True)
        expect(self.mixin._clobber).to.be.true()

    def test_assert_snapshot_match(self):
        file = NamedTemporaryFile(delete=False)
        snapshot = NamedTemporaryFile(delete=False)

        file.write('something')
        snapshot.write('something')
        file.close()
        snapshot.close()

        self.mixin._assert_snapshot_match(file.name, snapshot.name)
        expect(self.mixin.assertEqual).to.be.called_once_with(
            'something', 'something',
            msg='Snapshot does not match: %s !== %s' % (file.name, snapshot.name))

    def test_assert_snapshot_mismatch(self):
        file = NamedTemporaryFile(delete=False)
        snapshot = NamedTemporaryFile(delete=False)

        file.write('something')
        snapshot.write('some other thing')
        file.close()
        snapshot.close()

        self.mixin._assert_snapshot_match(file.name, snapshot.name)
        expect(self.mixin.assertEqual).to.be.called_once_with(
            'something', 'some other thing',
            msg='Snapshot does not match: %s !== %s' % (file.name, snapshot.name))

    @patch('snapshot_test.mixins.os.path.isfile')
    @patch('snapshot_test.mixins.open')
    def test_create_snapshot_wont_clobber(self, mock_open, mock_isfile):
        self.mixin._clobber = False
        mock_isfile.return_value = True
        self.mixin._create_snapshot('abc', 'def')
        expect(mock_open).not_to.be.called()

    def test_create_snapshot_clobber(self):
        self.mixin._clobber = True
        file = NamedTemporaryFile(delete=False)
        file.write('a')
        file.close()
        snapshot = NamedTemporaryFile(delete=False)
        snapshot.close()
        self.mixin._create_snapshot(file.name, snapshot.name)

        with open(snapshot.name) as snapshot_file:
            expect(snapshot_file.read()).to.eq('a')

    def test_create_snapshot_create_new(self):
        file = NamedTemporaryFile(delete=False)
        file.write('a')
        file.close()
        snapshot_path = '/tmp/tmp123/tmpabc'
        dirname = os.path.dirname(snapshot_path)
        if os.path.exists(dirname):
            shutil.rmtree(dirname)

        self.mixin._create_snapshot(file.name, snapshot_path)

        with open(snapshot_path) as snapshot_file:
            expect(snapshot_file.read()).to.eq('a')
