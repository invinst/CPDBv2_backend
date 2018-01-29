from cr.index_aliases import cr_index_alias
from cr.indexers import CRIndexer


class CRTestCaseMixin(object):
    def setUp(self):
        cr_index_alias.write_index.delete(ignore=404)
        cr_index_alias.read_index.create(ignore=400)

    def refresh_index(self):
        with cr_index_alias.indexing():
            CRIndexer().reindex()
        cr_index_alias.write_index.refresh()
