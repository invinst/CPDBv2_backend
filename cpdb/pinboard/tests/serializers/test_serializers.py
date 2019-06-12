from datetime import datetime

import pytz
from django.contrib.gis.geos import Point
from django.test import TestCase
from robber import expect

from data.factories import (
    AllegationCategoryFactory,
    AllegationFactory,
    VictimFactory,
)
from pinboard.serializers.cr_pinboard_serializer import CRPinboardSerializer
from pinboard.serializers.trr_pinboard_serializer import TRRPinboardSerializer
from trr.factories import TRRFactory


class CRPinboardSerializerTestCase(TestCase):
    def test_serialization(self):
        category = AllegationCategoryFactory(category='Use of Force', allegation_name='Subcategory')
        allegation = AllegationFactory(
            crid=123,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            most_common_category=category,
            coaccused_count=12,
            point=Point(-35.5, 68.9),
        )
        VictimFactory(
            gender='M',
            race='Black',
            age=35,
            allegation=allegation
        )

        expect(CRPinboardSerializer(allegation).data).to.eq({
            'date': '2002-01-01',
            'crid': '123',
            'category': 'Use of Force',
            'coaccused_count': 12,
            'kind': 'CR',
            'point': {
                'lon': -35.5,
                'lat': 68.9
            },
            'victims': [
                {
                    'gender': 'Male',
                    'race': 'Black',
                    'age': 35
                }
            ]
        })

    def test_get_point_none(self):
        allegation = AllegationFactory(crid=456, point=None)
        expect(CRPinboardSerializer(allegation).data).to.exclude('point')

    def test_serialization_no_point(self):
        category = AllegationCategoryFactory(category='Use of Force')
        allegation = AllegationFactory(
            crid=123,
            most_common_category=category,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            point=None,
            coaccused_count=12,
        )
        VictimFactory(
            gender='M',
            race='Black',
            age=35,
            allegation=allegation
        )

        expect(CRPinboardSerializer(allegation).data).to.eq({
            'date': '2002-01-01',
            'crid': '123',
            'category': 'Use of Force',
            'kind': 'CR',
            'coaccused_count': 12,
            'victims': [
                {
                    'gender': 'Male',
                    'race': 'Black',
                    'age': 35
                }
            ]
        })


class TRRPinboardSerializerTestCase(TestCase):
    def test_serialization(self):
        trr = TRRFactory(
            id=1,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
            taser=True,
            firearm_used=False,
        )

        expect(TRRPinboardSerializer(trr).data).to.eq({
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
        expect(TRRPinboardSerializer(trr).data).to.exclude('point')

    def test_serialization_no_point(self):
        trr = TRRFactory(
            id=1,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=None,
            taser=True,
            firearm_used=False,
        )

        expect(TRRPinboardSerializer(trr).data).to.eq({
            'trr_id': 1,
            'date': '2004-01-01',
            'kind': 'FORCE',
            'taser': True,
            'firearm_used': False,
        })
