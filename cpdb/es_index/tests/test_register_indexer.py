from django.test import SimpleTestCase

from robber import expect

from es_index import register_indexer, indexer_klasses, indexer_klasses_map


class RegisterIndexerTestCase(SimpleTestCase):
    def setUp(self):
        del indexer_klasses[:]

    def test_register_indexer(self):
        klass = '1'
        app_name = 'app'

        expect(register_indexer(app_name)(klass)).to.eq(klass)
        expect(indexer_klasses).to.eq([klass])
        expect(indexer_klasses_map[app_name]).to.eq([klass])
