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
    VictimFactory)
from social_graph.serializers.cr_detail_serializer import CRDetailSerializer


class CRDetailSerializerTestCase(TestCase):
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
        VictimFactory(
            gender='M',
            race='Black',
            age=35,
            allegation=allegation
        )

        expected_data = {
            'incident_date': '2002-01-01',
            'crid': '123',
            'category': 'Use of Force',
            'subcategory': 'Subcategory',
            'kind': 'CR',
            'address': '34XX Douglas Blvd',
            'to': '/complaint/123/',
            'victims': [
                {
                    'gender': 'Male',
                    'race': 'Black',
                    'age': 35,
                }
            ],
            'coaccused': [
                {
                    'id': 1,
                    'full_name': 'Jerome Finnigan',
                    'allegation_count': 20,
                    'percentile': {
                        'percentile_trr': '80.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',

                    }
                }
            ]
        }
        expect(CRDetailSerializer(allegation).data).to.eq(expected_data)
