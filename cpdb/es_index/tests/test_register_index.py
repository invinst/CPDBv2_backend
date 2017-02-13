from django.test import SimpleTestCase

from robber import expect

from es_index import register_index, index_klasses


class RegisterIndexTestCase(SimpleTestCase):
    def setUp(self):
        index_klasses.clear()

    def test_register_index(self):
        klass = 'A'

        expect(register_index(klass)).to.eq(klass)
        expect(index_klasses).to.eq(set([klass]))
