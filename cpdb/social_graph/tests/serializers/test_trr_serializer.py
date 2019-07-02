from datetime import datetime

import pytz
from django.contrib.gis.geos import Point
from django.test import TestCase
from robber import expect

from social_graph.serializers.trr_serializer import TRRSerializer
from trr.factories import TRRFactory


class TRRSerializerTestCase(TestCase):
    def test_serialization(self):
        trr = TRRFactory(
            id=1,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
            taser=True,
            firearm_used=False,
        )

        expect(TRRSerializer(trr).data).to.eq({
            'trr_id': 1,
            'date': '2004-01-01',
            'kind': 'FORCE',
            'taser': True,
            'firearm_used': False,
            'point': {
                'lon': -32.5,
                'lat': 61.3
            }
        })

    def test_get_point_none(self):
        trr = TRRFactory(id=2, point=None)
        expect(TRRSerializer(trr).data).to.exclude('point')

    def test_serialization_no_point(self):
        trr = TRRFactory(
            id=1,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=None,
            taser=True,
            firearm_used=False,
        )

        expect(TRRSerializer(trr).data).to.eq({
            'trr_id': 1,
            'date': '2004-01-01',
            'kind': 'FORCE',
            'taser': True,
            'firearm_used': False,
        })
