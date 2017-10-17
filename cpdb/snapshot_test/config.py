from django.conf import settings


test_snapshot_dir = getattr(settings, 'TEST_SNAPSHOT_DIR', 'test_snapshots')
