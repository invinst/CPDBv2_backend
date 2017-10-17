# Overview

Allow testing of binary files by retaining a copy of binary in question as "snapshot". Have a hard dependency on `django-nose`

# How to use `SnapshotTestMixin`

Put following properties in your settings file:

```
NOSE_PLUGINS = [
    'snapshot_test.plugins.CreateSnapshotPlugin'
]

TEST_SNAPSHOT_DIR = 'test_snapshots'  # optional
```

Use `SnapshotTestMixin` in your test like this:

```
from snapshot_test.mixins import SnapshotTestMixin

class MyTestCase(SnapshotTestMixin, StaticLiveServerTestCase):
    def test_my_binary(self):
        ...
        self.assert_snapshot_match('/path/to/my/binary', 'snapshotfilename')
```

Run your test like usual but add flag `--create-snapshot` to create snapshot instead of testing. Add flag `--snapshot-clobber` to clobber old snapshot.

```
cpdb/manage.py test --create-snapshot --snapshot-clobber
```

If there's no error you can run test like normal.

# Use `CleanupDirIfSuccessPlugin` in conjunction

It might be useful to cleanup directories only if tests succeed (and preserve if they fail because you want to inspect what's wrong). To do that, include `snapshot_test.plugins.CleanupDirIfSuccessPlugin` in `NOSE_PLUGINS`:

```
NOSE_PLUGINS = [
    ...
    'snapshot_test.plugins.CleanupDirIfSuccessPlugin'
]
```

and add `cleanupdirs` in your testcase:

```
class MyTestCase(...):
    cleanupdirs = ('/dir/to/cleanup/if/test/pass')
```
