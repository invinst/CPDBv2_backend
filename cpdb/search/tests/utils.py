from search.indices import autocompletes_alias
from search import es_client
from search.search_indexers import UnitOfficerIndexer, OfficerIndexer


class IndexMixin(object):
    def setUp(self):
        super(IndexMixin, self).setUp()
        autocompletes_alias.read_index.delete(ignore=404)
        autocompletes_alias.read_index.create(ignore=400)

    def rebuild_index(self):
        UnitOfficerIndexer(index_name='test_autocompletes').index_data()
        OfficerIndexer(index_name='test_autocompletes').index_data()

    def refresh_index(self):
        es_client.indices.refresh(index="test_autocompletes")
