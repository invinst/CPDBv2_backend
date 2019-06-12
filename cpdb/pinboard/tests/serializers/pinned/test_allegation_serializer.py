from datetime import datetime, date

from django.test import TestCase
from django.contrib.gis.geos import Point

import pytz
from robber import expect

from data.factories import (
    OfficerFactory,
    AllegationFactory,
    AllegationCategoryFactory,
    OfficerAllegationFactory,
    VictimFactory,
)

from pinboard.serializers.pinned import PinnedAllegationSerializer


class PinnedAllegationSerializerTestCase(TestCase):
    def test_serialization(self):
        category = AllegationCategoryFactory(category='Use of Force', allegation_name='Subcategory')
        category2 = AllegationCategoryFactory(category='Verbal Abuse', allegation_name='Miscellaneous')
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
        coaccused = OfficerFactory(
            id=2,
            first_name='Walter',
            last_name='White',
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
            recc_outcome='11 Day Suspension',
            final_outcome='Separation',
            final_finding='SU',
            allegation_category=category2,
            disciplined=True,
        )

        expect(PinnedAllegationSerializer(allegation).data).to.eq({
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
            'coaccused': [{
                'id': 2,
                'full_name': 'Walter White',
                'complaint_count': 6,
                'sustained_count': 5,
                'birth_year': 1940,
                'complaint_percentile': 0.0,
                'recommended_outcome': '11 Day Suspension',
                'final_outcome': 'Separation',
                'final_finding': 'Sustained',
                'category': 'Verbal Abuse',
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
                }
            }],
        })
