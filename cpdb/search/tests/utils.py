from search.indices import autocompletes
from search import es_client


class IndexMixin(object):
    def setUp(self):
        super(IndexMixin, self).setUp()
        autocompletes.delete(ignore=404)
        autocompletes.create()

    def refresh_index(self):
        es_client.indices.refresh(index="test_autocompletes")
