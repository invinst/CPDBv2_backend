from datetime import datetime

from django.test import TestCase

from robber import expect
import pytz

from data.factories import AllegationFactory
from search.serializers import AllegationSerializer


class AllegationSerializerTestCase(TestCase):
    def test_serialization(self):
        allegation = AllegationFactory(
            crid='C12345',
            incident_date=datetime(2007, 1, 1, tzinfo=pytz.utc),
        )

        expect(AllegationSerializer(allegation).data).to.eq({
            'id': 'C12345',
            'crid': 'C12345',
            'incident_date': '2007-01-01',
            'type': 'CR',
            'category': 'Unknown'
        })
