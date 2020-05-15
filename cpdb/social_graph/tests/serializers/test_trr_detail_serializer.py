from datetime import datetime

import pytz
from django.contrib.gis.geos import Point
from django.test import TestCase
from robber import expect

from data.factories import OfficerFactory
from social_graph.serializers import TRRDetailSerializer
from trr.factories import TRRFactory


class TRRDetailSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=20,
            trr_percentile=80,
            complaint_percentile=85,
            civilian_allegation_percentile=90,
            internal_allegation_percentile=95
        )
        trr = TRRFactory(
            id=123456,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
            taser=True,
            firearm_used=False,
            block='34XX',
            street='Douglas Blvd',
            officer=officer,
        )

        expect(TRRDetailSerializer(trr).data).to.eq({
            'kind': 'FORCE',
            'trr_id': 123456,
            'to': '/trr/123456/',
            'taser': True,
            'firearm_used': False,
            'date': '2004-01-01',
            'address': '34XX Douglas Blvd',
            'officer': {
                'id': 8562,
                'full_name': 'Jerome Finnigan',
                'allegation_count': 20,
                'percentile_trr': '80.0000',
                'percentile_allegation': '85.0000',
                'percentile_allegation_civilian': '90.0000',
                'percentile_allegation_internal': '95.0000',
            },
        })
