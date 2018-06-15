from trr.index_aliases import trr_index_alias
from trr.indexers import TRRIndexer


class TRRTestCaseMixin(object):
    def setUp(self):
        trr_index_alias.write_index.delete(ignore=404)
        trr_index_alias.read_index.create(ignore=400)

    def refresh_index(self):
        with trr_index_alias.indexing():
            TRRIndexer().reindex()
        trr_index_alias.write_index.refresh()
