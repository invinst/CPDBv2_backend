from django.test import SimpleTestCase

from robber import expect

from es_index import register_indexer, indexer_klasses


class RegisterIndexerTestCase(SimpleTestCase):
    def setUp(self):
        indexer_klasses.clear()

    def test_register_indexer(self):
        klass = 1

        expect(register_indexer(klass)).to.eq(klass)
        expect(indexer_klasses).to.eq(set([klass]))
