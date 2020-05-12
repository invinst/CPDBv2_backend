from datetime import datetime

import pytz
from django.test import TestCase
from robber import expect

from data.factories import OfficerFactory
from social_graph.serializers.officer_percentile_serializer import OfficerPercentileSerializer


class OfficerAllegationPercentileSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=1,
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=20,
            sustained_count=10,
            birth_year=1980,
            race='Asian',
            gender='M',
            rank='Police Officer',
            resignation_date=datetime(2000, 1, 1, tzinfo=pytz.utc),
            trr_percentile=80,
            complaint_percentile=85,
            civilian_allegation_percentile=90,
            internal_allegation_percentile=95

        )
        expect(OfficerPercentileSerializer(officer).data).to.eq({
            'percentile_trr': '80.0000',
            'percentile_allegation': '85.0000',
            'percentile_allegation_civilian': '90.0000',
            'percentile_allegation_internal': '95.0000',
        })
