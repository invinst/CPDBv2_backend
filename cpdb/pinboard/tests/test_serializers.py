from datetime import datetime

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
import pytz

from data.factories import AllegationCategoryFactory, AllegationFactory
from pinboard.serializers.cr_pinboard_serializer import CRPinboardSerializer
from pinboard.serializers.trr_pinboard_serializer import TRRPinboardSerializer
from trr.factories import TRRFactory


class CRPinboardSerializerTestCase(TestCase):
    def test_serialization(self):
        category = AllegationCategoryFactory(category='Use of Force')
        allegation = AllegationFactory(
            crid=123,
            most_common_category=category,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            point=Point(-35.5, 68.9),
        )

        expect(CRPinboardSerializer(allegation).data).to.eq({
            'date': '2002-01-01',
            'crid': '123',
            'category': 'Use of Force',
            'kind': 'CR',
            'point': {
                'lon': -35.5,
                'lat': 68.9
            }
        })


class TRRPinboardSerializerTestCase(TestCase):
    def test_serialization(self):
        trr = TRRFactory(
            id=1,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
        )

        expect(TRRPinboardSerializer(trr).data).to.eq({
            'trr_id': 1,
            'date': '2004-01-01',
            'kind': 'FORCE',
            'point': {
                'lon': -32.5,
                'lat': 61.3
            }
        })
