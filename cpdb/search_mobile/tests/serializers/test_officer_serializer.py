from django.test import TestCase

from robber import expect

from data.factories import OfficerFactory
from search_mobile.serializers import OfficerSerializer


class OfficerSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=1,
            first_name='Jerome',
            last_name='Finnigan',
            current_badge='123456',
        )

        expect(OfficerSerializer(officer).data).to.eq({
            'id': 1,
            'name': 'Jerome Finnigan',
            'badge': '123456',
            'type': 'OFFICER',
        })
