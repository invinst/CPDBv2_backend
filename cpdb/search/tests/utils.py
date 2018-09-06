from search.indices import autocompletes_alias
from search import es_client
from officers.index_aliases import officers_index_alias
from officers.indexers import OfficersIndexer
from search.search_indexers import IndexerManager
from search.constants import DEFAULT_INDEXERS


class IndexMixin(object):
    def setUp(self):
        super(IndexMixin, self).setUp()
        autocompletes_alias.read_index.delete(ignore=404)
        autocompletes_alias.read_index.create(ignore=400)

        officers_index_alias.read_index.delete(ignore=404)
        officers_index_alias.read_index.create(ignore=400)

    def rebuild_index(self):
        with officers_index_alias.indexing():
            OfficersIndexer().reindex()

        IndexerManager(indexers=DEFAULT_INDEXERS).rebuild_index()

    def refresh_index(self):
        officers_index_alias.read_index.refresh()
        es_client.indices.refresh(index="test_autocompletes")
