from django.test import TestCase

from mock import Mock
from robber import expect

from data.factories import OfficerFactory
from twitterbot.indexers import OfficerIndexer


class OfficerIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer = OfficerFactory()
        expect([obj.pk for obj in OfficerIndexer().get_queryset()]).to.eq([officer.pk])

    def test_extract_datum(self):
        indexer = OfficerIndexer()
        expect(indexer.extract_datum(Mock(id=123, allegation_count=3, full_name='John Doe'))).to.eq({
            'id': 123,
            'full_name': 'John Doe',
            'allegation_count': 3
        })
