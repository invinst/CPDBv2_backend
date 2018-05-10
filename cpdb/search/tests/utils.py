from search.indices import autocompletes_alias
from search import es_client
from search.search_indexers import UnitOfficerIndexer

from officers.index_aliases import officers_index_alias
from officers.indexers import OfficersIndexer


class IndexMixin(object):
    def setUp(self):
        super(IndexMixin, self).setUp()
        autocompletes_alias.read_index.delete(ignore=404)
        autocompletes_alias.read_index.create(ignore=400)

        officers_index_alias.read_index.delete(ignore=404)
        officers_index_alias.read_index.create(ignore=400)

    def rebuild_index(self):
        UnitOfficerIndexer(index_name='test_autocompletes').index_data()
        with officers_index_alias.indexing():
            OfficersIndexer().reindex()

    def refresh_index(self):
        officers_index_alias.read_index.refresh()
        es_client.indices.refresh(index="test_autocompletes")
