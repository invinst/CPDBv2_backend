from datetime import datetime

from django.contrib.gis.geos import Point
from django.test import TestCase

import pytz
from robber import expect

from data.factories import OfficerFactory
from pinboard.serializers.desktop.pinned.trr_serializer import TRRSerializer
from trr.factories import TRRFactory, ActionResponseFactory


class PinnedTRRSerializerTestCase(TestCase):
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

        trr = TRRFactory(
            id=123456,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(1.0, 1.0),
            taser=True,
            firearm_used=False,
            block='34XX',
            street='Douglas Blvd',
            officer=officer,
        )

        ActionResponseFactory(trr=trr, force_type='Impact Weapon', action_sub_category='2')

        expect(TRRSerializer(trr).data).to.eq({
            'id': 123456,
            'trr_datetime': '2004-01-01',
            'category': 'Impact Weapon',
            'point': {'lon': 1.0, 'lat': 1.0},
            'to': '/trr/123456/',
            'taser': True,
            'firearm_used': False,
            'address': '34XX Douglas Blvd',
            'officer': {
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
            },
        })
