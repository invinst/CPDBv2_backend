from es_index import es_client
from cr.indices import cr_index
from cr.indexers import CRIndexer


class CRTestCaseMixin(object):
    def setUp(self):
        cr_index.delete(ignore=404)
        cr_index.create()

    def refresh_index(self):
        CRIndexer().reindex()
        es_client.indices.refresh(index='test_cr')
