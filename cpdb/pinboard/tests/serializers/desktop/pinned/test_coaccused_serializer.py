from datetime import datetime

import pytz
from django.test import TestCase

from robber import expect

from data.factories import OfficerFactory
from pinboard.serializers.desktop.pinned.coaccused_serializer import CoaccusedSerializer


class CoaccusedSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=8562,
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
        expect(CoaccusedSerializer(officer).data).to.eq({
            'id': 8562,
            'full_name': 'Jerome Finnigan',
            'complaint_count': 20,
            'sustained_count': 10,
            'birth_year': 1980,
            'complaint_percentile': 85,
            'race': 'Asian',
            'gender': 'Male',
            'rank': 'Police Officer',
            'percentile': {
                'percentile_allegation': '85.0000',
                'percentile_trr': '80.0000',
                'percentile_allegation_civilian': '90.0000',
                'percentile_allegation_internal': '95.0000',
            },
        })
