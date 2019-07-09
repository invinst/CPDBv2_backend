import pytz
from datetime import datetime

from django.test import TestCase

from robber import expect

from social_graph.serializers.accused_serializer import AccusedSerializer


class AccusedSerializerTestCase(TestCase):
    def test_serialization(self):
        class Accused(object):
            def __init__(self, officer_id_1, officer_id_2, incident_date, accussed_count):
                self.officer_id_1 = officer_id_1
                self.officer_id_2 = officer_id_2
                self.incident_date = incident_date
                self.accussed_count = accussed_count

        accused = Accused(
            officer_id_1=1,
            officer_id_2=2,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc),
            accussed_count=3,
        )

        expect(AccusedSerializer(accused).data).to.eq({
            'officer_id_1': 1,
            'officer_id_2': 2,
            'incident_date': '2005-12-31',
            'accussed_count': 3,
        })
