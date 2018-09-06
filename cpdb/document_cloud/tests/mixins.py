from cr.index_aliases import cr_index_alias
from cr.indexers import CRIndexer
from officers.index_aliases import officers_index_alias
from officers.indexers import CRNewTimelineEventIndexer


class DocumentcloudTestCaseMixin(object):
    def setUp(self):
        cr_index_alias.write_index.delete(ignore=404)
        cr_index_alias.read_index.delete(ignore=404)
        cr_index_alias.read_index.create(ignore=400)

        officers_index_alias.write_index.delete(ignore=404)
        officers_index_alias.read_index.delete(ignore=404)
        officers_index_alias.read_index.create(ignore=400)

    def rebuild_index(self):
        with cr_index_alias.indexing():
            CRIndexer().reindex()

        with officers_index_alias.indexing():
            CRNewTimelineEventIndexer().reindex()

    def refresh_index(self):
        cr_index_alias.read_index.refresh()
        officers_index_alias.read_index.refresh()
