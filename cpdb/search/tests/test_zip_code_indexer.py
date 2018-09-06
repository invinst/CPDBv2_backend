from django.test import SimpleTestCase
from mock import patch
from robber import expect

from search.search_indexers import ZipCodeIndexer
from search.utils import ZipCode


class ZipCodeIndexerTestCase(SimpleTestCase):
    @patch('search.search_indexers.chicago_zip_codes')
    def test_get_query_set(self, chicago_zip_codes_mock):
        ZipCodeIndexer().get_queryset()
        expect(chicago_zip_codes_mock).to.be.called_once()

    def test_extract_datum(self):
        zip_code = ZipCode(pk=1, zip_code='123456', url='cpdp.co')
        expect(ZipCodeIndexer().extract_datum(zip_code)).to.eq({
            'id': 1,
            'zip_code': '123456',
            'url': 'cpdp.co',
            'tags': ['zip code']
        })
