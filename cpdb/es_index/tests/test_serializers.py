from datetime import date

from django.test import SimpleTestCase

from robber import expect

from es_index.serializers import (
    BaseSerializer, get, get_date, get_gender, literal
)


class BaseSerializerTestCase(SimpleTestCase):
    def setUp(self):
        class Serializer(BaseSerializer):
            def __init__(self, *args, **kwargs):
                super(Serializer, self).__init__(*args, **kwargs)
                self._fields = {
                    'name': get('first_name')
                }

        self.serializer = Serializer(key='key')

    def test_serialize(self):
        expect(self.serializer.serialize({'first_name': 'Jerome'})).to.eq({
            'name': 'Jerome'
        })

    def test_call(self):
        expect(self.serializer({'key': [
            {'first_name': 'James'},
            {'first_name': 'John'}
        ]})).to.eq([
            {'name': 'James'},
            {'name': 'John'}
        ])


class SerializerTestCase(SimpleTestCase):
    def test_get(self):
        expect(get('name')({'name': 'Jerome'})).to.eq('Jerome')

    def test_get_date(self):
        expect(
            get_date('start_date')({'start_date': date(2016, 4, 5)})
        ).to.eq('2016-04-05')

        expect(
            get_date('start_date')({'start_date': None})
        ).to.be.none()

    def test_get_gender(self):
        expect(
            get_gender('gender')({'gender': 'M'})
        ).to.eq('Male')

        expect(
            get_gender('gender')({'gender': 'F'})
        ).to.eq('Female')

    def test_literal(self):
        expect(literal('string')({})).to.eq('string')
        expect(literal(123)({})).to.eq(123)
