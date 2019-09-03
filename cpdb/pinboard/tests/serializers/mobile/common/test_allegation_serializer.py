from datetime import datetime

from django.contrib.gis.geos import Point
from django.test import TestCase

import pytz
from robber import expect

from data.factories import (
    AllegationCategoryFactory,
    AllegationFactory,
)

from pinboard.serializers.mobile.common import AllegationMobileSerializer


class AllegationMobileSerializerTestCase(TestCase):
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

        expect(AllegationMobileSerializer(allegation).data).to.eq({
            'crid': '123',
            'category': 'Use of Force',
            'incident_date': '2002-01-01',
            'point': {
                'lon': -35.5,
                'lat': 68.9
            },
        })

    def test_get_category(self):
        allegation = AllegationFactory(most_common_category=None)
        serializer = AllegationMobileSerializer(allegation)
        expect(serializer.data['category']).to.eq('Unknown')
