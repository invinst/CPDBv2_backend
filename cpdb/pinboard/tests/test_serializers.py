from datetime import datetime, date

import pytz
from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework.test import APITestCase
from robber import expect

from data.factories import (
    AllegationCategoryFactory,
    AllegationFactory,
    VictimFactory,
    OfficerFactory,
    OfficerAllegationFactory,
)
from data.models import Allegation
from pinboard.serializers.cr_pinboard_serializer import CRPinboardSerializer
from pinboard.serializers.pinboard_complaint_serializer import PinboardComplaintSerializer
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


class PinboardComplaintSerializerTestCase(APITestCase):
    def test_get_point_none(self):
        allegation = Allegation(point=None)
        serializer = PinboardComplaintSerializer(allegation)
        expect(serializer.data['point']).to.eq(None)

    def test_get_most_common_category_none(self):
        allegation = Allegation(most_common_category=None)
        serializer = PinboardComplaintSerializer(allegation)
        expect(serializer.data['most_common_category']).to.eq('Unknown')

    def test_get_sub_category_none(self):
        allegation = Allegation(most_common_category=None)
        serializer = PinboardComplaintSerializer(allegation)
        expect(serializer.data['sub_category']).to.eq('Unknown')

    def test_get_address(self):
        allegation = Allegation(
            old_complaint_address=None,
            add1='3510',
            add2='Michian Ave',
            city='Chicago'
        )
        serializer = PinboardComplaintSerializer(allegation)
        expect(serializer.data['address']).to.eq('3510 Michian Ave, Chicago')

    def test_get_serialized(self):
        category = AllegationCategoryFactory(
            category='Use of Force',
            allegation_name='Subcategory'
        )

        allegation = AllegationFactory(
            crid='123',
            old_complaint_address='16XX N TALMAN AVE, CHICAGO IL',
            most_common_category=category,
            point=Point(-35.5, 68.9),
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
        )

        coaccused = OfficerFactory(
            id=1,
            first_name='German',
            last_name='Mack',
            allegation_count=6,
            sustained_count=5,
            birth_year=1940,
            race='White',
            gender='M',
            rank='Sergeant of Police',
            complaint_percentile=0.0,
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
            resignation_date=date(2015, 4, 14)
        )

        OfficerAllegationFactory(
            officer=coaccused,
            allegation=allegation,
            recc_outcome='10 Day Suspension',
            final_outcome='Separation',
            final_finding='SU',
            allegation_category=category,
            disciplined=True,
        )

        VictimFactory(
            allegation=allegation,
            gender='M',
            race='White',
            age=40,
        )

        expect(PinboardComplaintSerializer(allegation).data).to.eq({
            'address': '16XX N TALMAN AVE, CHICAGO IL',
            'coaccused': [{
                'id': 1,
                'full_name': 'German Mack',
                'complaint_count': 6,
                'sustained_count': 5,
                'birth_year': 1940,
                'complaint_percentile': 0.0,
                'recommended_outcome': '10 Day Suspension',
                'final_outcome': 'Separation',
                'final_finding': 'Sustained',
                'category': 'Use of Force',
                'disciplined': True,
                'race': 'White',
                'gender': 'Male',
                'rank': 'Sergeant of Police',
                'percentile': {
                    'year': 2015,
                    'percentile_trr': '3.3000',
                    'percentile_allegation': '0.0000',
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000'
                },
            }],
            'sub_category': 'Subcategory',
            'to': '/complaint/123/',
            'crid': '123',
            'incident_date': '2002-01-01',
            'point': {'lon': -35.5, 'lat': 68.9},
            'most_common_category': 'Use of Force',
            'victims': [{
                'gender': 'Male',
                'race': 'White',
                'age': 40,
            }],
        })
