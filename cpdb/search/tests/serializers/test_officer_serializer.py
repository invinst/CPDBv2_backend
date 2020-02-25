from django.test import TestCase

from robber import expect

from data.factories import OfficerFactory
from search.serializers import OfficerSerializer


class OfficerSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=1,
            first_name='Jerome',
            last_name='Finnigan',
            current_badge='123456',
            allegation_count=20,
            sustained_count=5,
            birth_year=1980,
            race='White',
            gender='M',
            rank='Police Officer'
        )

        expect(OfficerSerializer(officer).data).to.eq({
            'id': 1,
            'name': 'Jerome Finnigan',
            'race': 'White',
            'gender': 'Male',
            'allegation_count': 20,
            'sustained_count': 5,
            'birth_year': 1980,
            'type': 'OFFICER',
            'rank': 'Police Officer'
        })
