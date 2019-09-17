from tracker.index_aliases import tracker_index_alias
from tracker.indexers import AttachmentFileIndexer


class TrackerTestCaseMixin(object):
    def setUp(self):
        tracker_index_alias.write_index.delete(ignore=404)
        tracker_index_alias.read_index.create(ignore=400)

    def refresh_index(self):
        with tracker_index_alias.indexing():
            AttachmentFileIndexer().reindex()
        tracker_index_alias.write_index.refresh()
