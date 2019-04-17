from datetime import datetime

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
import pytz

from data.factories import AllegationFactory, OfficerFactory, OfficerAllegationFactory, AllegationCategoryFactory, \
    VictimFactory
from pinboard.queries import GeographyDataQuery
from trr.factories import TRRFactory


class GeographyDataQueryTestCase(TestCase):
    def test_execute(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)
        officers = [officer_1, officer_2, officer_3, officer_4]

        category_1 = AllegationCategoryFactory(category='Use of Force')
        category_2 = AllegationCategoryFactory(category='Illegal Search')
        allegation_1 = AllegationFactory(
            crid=123,
            most_common_category=category_1,
            coaccused_count=15,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            point=Point(-35.5, 68.9),
        )
        allegation_2 = AllegationFactory(
            crid=456,
            most_common_category=category_2,
            coaccused_count=20,
            incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc),
            point=Point(37.3, 86.2),
        )
        VictimFactory(
            gender='M',
            race='Black',
            age=35,
            allegation=allegation_1
        )
        VictimFactory(
            gender='F',
            race='White',
            age=40,
            allegation=allegation_2
        )
        OfficerAllegationFactory(officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(officer=officer_2, allegation=allegation_2)

        TRRFactory(
            id=1,
            officer=officer_3,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
            taser=True,
            firearm_used=False,
        )
        TRRFactory(
            id=2,
            officer=officer_4,
            trr_datetime=datetime(2005, 1, 1, tzinfo=pytz.utc),
            point=Point(33.3, 78.4),
            taser=False,
            firearm_used=True,
        )

        expected_data = [
            {
                'date': '2002-01-01',
                'crid': '123',
                'category': 'Use of Force',
                'coaccused_count': 15,
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
            },
            {
                'date': '2003-01-01',
                'crid': '456',
                'category': 'Illegal Search',
                'coaccused_count': 20,
                'kind': 'CR',
                'point': {
                    'lon': 37.3,
                    'lat': 86.2
                },
                'victims': [
                    {
                        'gender': 'Female',
                        'race': 'White',
                        'age': 40
                    }
                ]
            },
            {
                'trr_id': 1,
                'date': '2004-01-01',
                'kind': 'FORCE',
                'taser': True,
                'firearm_used': False,
                'point': {
                    'lon': -32.5,
                    'lat': 61.3
                }
            },
            {
                'trr_id': 2,
                'date': '2005-01-01',
                'kind': 'FORCE',
                'taser': False,
                'firearm_used': True,
                'point': {
                    'lon': 33.3,
                    'lat': 78.4
                }
            },
        ]

        results = GeographyDataQuery(officers).execute()

        expect(len(results)).to.eq(len(expected_data))

        for data in expected_data:
            expect(results).to.contain(data)
