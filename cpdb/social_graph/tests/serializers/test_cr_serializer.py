from datetime import datetime

import pytz
from django.contrib.gis.geos import Point
from django.test import TestCase
from robber import expect

from data.factories import (
    AllegationCategoryFactory,
    AllegationFactory,
    OfficerFactory,
    OfficerAllegationFactory,
)
from social_graph.serializers.cr_serializer import CRSerializer


class CRSerializerTestCase(TestCase):
    def test_serialization(self):
        category = AllegationCategoryFactory(category='Use of Force', allegation_name='Subcategory')
        allegation = AllegationFactory(
            crid=123,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            most_common_category=category,
            coaccused_count=12,
            point=Point(-35.5, 68.9),
            old_complaint_address='34XX Douglas Blvd'
        )
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
        OfficerAllegationFactory(
            officer=officer,
            allegation=allegation,
            recc_outcome='Separation',
            final_outcome='30 Day Suspension',
            final_finding='UN',
            allegation_category=category,
            disciplined=True
        )

        expected_data = {
            'date': '2002-01-01',
            'crid': '123',
            'category': 'Use of Force',
            'kind': 'CR',
            'point': {
                'lon': -35.5,
                'lat': 68.9
            },
        }
        expect(CRSerializer(allegation).data).to.eq(expected_data)

    def test_get_point_none(self):
        allegation = AllegationFactory(crid=456, point=None)
        expect(CRSerializer(allegation).data).to.exclude('point')

    def test_serialization_no_point(self):
        category = AllegationCategoryFactory(category='Use of Force', allegation_name='Miscellaneous')
        allegation = AllegationFactory(
            crid=123,
            most_common_category=category,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            point=None,
            coaccused_count=12,
        )

        expect(CRSerializer(allegation).data).to.eq({
            'date': '2002-01-01',
            'crid': '123',
            'category': 'Use of Force',
            'kind': 'CR',
        })
