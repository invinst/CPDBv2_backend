from search.indices import autocompletes
from search import es_client
from search.search_indexers import UnitOfficerIndexer, OfficerIndexer


class IndexMixin(object):
    def setUp(self):
        super(IndexMixin, self).setUp()
        autocompletes.delete(ignore=404)
        autocompletes.create()

    def rebuild_index(self):
        UnitOfficerIndexer().index_data()
        OfficerIndexer().index_data()

    def refresh_index(self):
        es_client.indices.refresh(index="test_autocompletes")
