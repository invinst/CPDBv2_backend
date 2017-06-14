from django.test import SimpleTestCase

from robber import expect

from es_index import register_index, index_klasses, index_klasses_map


class RegisterIndexTestCase(SimpleTestCase):
    def setUp(self):
        index_klasses.clear()

    def test_register_index(self):
        klass = 'A'
        app_name = 'app'

        expect(register_index(app_name)(klass)).to.eq(klass)
        expect(index_klasses).to.eq(set([klass]))
        expect(index_klasses_map[app_name]).to.eq(set([klass]))
