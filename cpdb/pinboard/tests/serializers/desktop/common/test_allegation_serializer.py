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
from data.models import Allegation

from pinboard.serializers.desktop.common import AllegationSerializer


class AllegationSerializerTestCase(TestCase):
    def test_serialization(self):
        category = AllegationCategoryFactory(category='Use of Force', allegation_name='Subcategory')
        allegation = AllegationFactory(
            crid=123,
            old_complaint_address='16XX N TALMAN AVE, CHICAGO IL',
            most_common_category=category,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            coaccused_count=12,
            point=Point(-35.5, 68.9),
        )
        VictimFactory(
            gender='M',
            race='Black',
            age=35,
            allegation=allegation
        )

        expect(AllegationSerializer(allegation).data).to.eq({
            'crid': '123',
            'address': '16XX N TALMAN AVE, CHICAGO IL',
            'category': 'Use of Force',
            'incident_date': '2002-01-01',
            'victims': [
                {
                    'gender': 'Male',
                    'race': 'Black',
                    'age': 35
                }
            ],
            'point': {
                'lon': -35.5,
                'lat': 68.9
            },
            'to': '/complaint/123/',
            'sub_category': 'Subcategory',
        })

    def test_get_address(self):
        allegation = Allegation(
            old_complaint_address=None,
            add1='3510',
            add2='Michian Ave',
            city='Chicago'
        )
        serializer = AllegationSerializer(allegation)
        expect(serializer.data['address']).to.eq('3510 Michian Ave, Chicago')

    def test_get_category(self):
        allegation = AllegationFactory(most_common_category=None)
        serializer = AllegationSerializer(allegation)
        expect(serializer.data['category']).to.eq('Unknown')

    def test_sub_category(self):
        allegation = AllegationFactory(most_common_category=None)
        serializer = AllegationSerializer(allegation)
        expect(serializer.data['sub_category']).to.eq('Unknown')
