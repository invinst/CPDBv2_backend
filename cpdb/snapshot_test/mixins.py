import inspect
import sys
import os

from django.apps import apps

from .config import test_snapshot_dir


class SnapshotTestMixin:
    _is_creating_snapshot = False
    _clobber = False
    _app_paths = [app_config.path for app_config in apps.get_app_configs()]

    def assert_snapshot_match(self, file_path, snapshot_path):
        snapshot_path = self.full_snapshot_path(snapshot_path)
        if self._is_creating_snapshot:
            self._create_snapshot(file_path, snapshot_path)
        else:
            self._assert_snapshot_match(file_path, snapshot_path)

    def full_snapshot_path(self, path):
        file_path = inspect.getfile(sys.modules[self.__class__.__module__])
        app_path = next(path for path in self._app_paths if file_path.startswith(path))
        return os.path.join(app_path, test_snapshot_dir, path)

    def enable_create_snapshot_mode(self):
        self._is_creating_snapshot = True

    def set_clobber(self, clobber):
        self._clobber = clobber

    def _create_snapshot(self, file_path, snapshot_path):
        if not self._clobber and os.path.isfile(snapshot_path):
            return
        try:
            os.makedirs(os.path.dirname(snapshot_path))
        except OSError:
            pass
        with open(file_path) as file:
            with open(snapshot_path, 'w') as snapshot_file:
                snapshot_file.write(file.read())

    def _assert_snapshot_match(self, file_path, snapshot_path):
        with open(file_path) as file:
            with open(snapshot_path) as snapshot:
                self.assertEqual(
                    file.read(), snapshot.read(),
                    msg='Snapshot does not match: %s !== %s' % (file_path, snapshot_path))
