from datetime import date

from django.test import SimpleTestCase
from django.contrib.gis.geos import Point

from robber import expect

from es_index.serializers import (
    BaseSerializer, get, get_date, get_gender, literal, get_age_range,
    get_finding, get_point
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

        expect(
            get_gender('gender')({'gender': None})
        ).to.be.none()

        expect(
            get_gender('gender', 'Unknown')({'gender': None})
        ).to.eq('Unknown')

    def test_literal(self):
        expect(literal('string')({})).to.eq('string')
        expect(literal(123)({})).to.eq(123)

    def test_get_age_range(self):
        func = get_age_range([20, 30, 40], 'age')
        expect(func({'age': 18})).to.eq('<20')
        expect(func({'age': 20})).to.eq('20-30')
        expect(func({'age': 22})).to.eq('20-30')
        expect(func({'age': 34})).to.eq('30-40')
        expect(func({'age': 46})).to.eq('40+')
        expect(func({'age': None})).to.eq(None)

        expect(
            get_age_range([20, 30, 40], 'age', 'Unknown')({'age': None})
        ).to.eq('Unknown')

    def test_get_finding(self):
        func = get_finding('final_finding')
        expect(func({'final_finding': 'UN'})).to.eq('Unfounded')
        expect(func({'final_finding': None})).to.eq(None)
        expect(
            get_finding('final_finding', 'Unknown')({'final_finding': None})
        ).to.eq('Unknown')

    def test_get_point(self):
        func = get_point('point')
        expect(func({'point': Point(1, 2)})).to.eq({
            'lon': 1, 'lat': 2
        })
        expect(func({})).to.eq(None)
        expect(func({'point': None})).to.eq(None)
        expect(
            get_point('point', 'Unknown')({'point': None})
        ).to.eq('Unknown')
