from datetime import datetime
from operator import itemgetter

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
import pytz

from data.factories import AllegationFactory, OfficerFactory, OfficerAllegationFactory, AllegationCategoryFactory, \
    VictimFactory
from social_graph.queries.geographic_data_query import GeographyDataQuery
from trr.factories import TRRFactory


class GeographyDataQueryTestCase(TestCase):
    def test_execute_with_detail_is_false(self):
        officer_1 = OfficerFactory(
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
        officer_2 = OfficerFactory(
            id=2,
            first_name='Edward',
            last_name='May',
            allegation_count=10,
            sustained_count=5,
            birth_year=1970,
            race='Black',
            gender='M',
            rank='Police Officer',
            resignation_date=datetime(2000, 1, 1, tzinfo=pytz.utc),
            trr_percentile=50,
            complaint_percentile=55,
            civilian_allegation_percentile=60,
            internal_allegation_percentile=65

        )
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)
        officers = [officer_1, officer_2, officer_3, officer_4]

        category_1 = AllegationCategoryFactory(category='Use of Force', allegation_name='Subcategory 1')
        category_2 = AllegationCategoryFactory(category='Illegal Search', allegation_name='Subcategory 2')
        allegation_1 = AllegationFactory(
            crid=123,
            most_common_category=category_1,
            coaccused_count=15,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            point=Point(-35.5, 68.9),
            old_complaint_address='34XX Douglas Blvd',
        )
        allegation_2 = AllegationFactory(
            crid=456,
            most_common_category=category_2,
            coaccused_count=20,
            incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc),
            point=Point(37.3, 86.2),
            old_complaint_address='34XX Douglas Blvd',
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
        OfficerAllegationFactory(
            officer=officer_1,
            allegation=allegation_1,
            recc_outcome='Separation',
            final_outcome='30 Day Suspension',
            final_finding='UN',
            allegation_category=category_1,
            disciplined=True
        )
        OfficerAllegationFactory(
            officer=officer_1,
            allegation=allegation_2,
            recc_outcome='Separation',
            final_outcome='28 Day Suspension',
            final_finding='UN',
            allegation_category=category_2,
            disciplined=True
        )
        OfficerAllegationFactory(
            officer=officer_2,
            allegation=allegation_2,
            recc_outcome='Separation',
            final_outcome='Suspended Over 30 Days',
            final_finding='SU',
            allegation_category=category_2,
            disciplined=True
        )

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
                'kind': 'CR',
                'point': {
                    'lon': -35.5,
                    'lat': 68.9
                },
            },
            {
                'date': '2003-01-01',
                'crid': '456',
                'category': 'Illegal Search',
                'kind': 'CR',
                'point': {
                    'lon': 37.3,
                    'lat': 86.2
                },
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

    def test_execute_with_detail_is_true(self):
        officer_1 = OfficerFactory(
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
        officer_2 = OfficerFactory(
            id=2,
            first_name='Edward',
            last_name='May',
            allegation_count=10,
            sustained_count=5,
            birth_year=1970,
            race='Black',
            gender='M',
            rank='Police Officer',
            resignation_date=datetime(2000, 1, 1, tzinfo=pytz.utc),
            trr_percentile=50,
            complaint_percentile=55,
            civilian_allegation_percentile=60,
            internal_allegation_percentile=65

        )
        officer_3 = OfficerFactory(
            id=3,
            first_name='Jon',
            last_name='Snow',
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
        officer_4 = OfficerFactory(
            id=4,
            first_name='David',
            last_name='May',
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
        officers = [officer_1, officer_2, officer_3, officer_4]

        category_1 = AllegationCategoryFactory(category='Use of Force', allegation_name='Subcategory 1')
        category_2 = AllegationCategoryFactory(category='Illegal Search', allegation_name='Subcategory 2')
        allegation_1 = AllegationFactory(
            crid=123,
            most_common_category=category_1,
            coaccused_count=15,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            point=Point(-35.5, 68.9),
            old_complaint_address='34XX Douglas Blvd',
        )
        allegation_2 = AllegationFactory(
            crid=456,
            most_common_category=category_2,
            coaccused_count=20,
            incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc),
            point=Point(37.3, 86.2),
            old_complaint_address='34XX Douglas Blvd',
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
        OfficerAllegationFactory(
            officer=officer_1,
            allegation=allegation_1,
            recc_outcome='Separation',
            final_outcome='30 Day Suspension',
            final_finding='UN',
            allegation_category=category_1,
            disciplined=True
        )
        OfficerAllegationFactory(
            officer=officer_1,
            allegation=allegation_2,
            recc_outcome='Separation',
            final_outcome='28 Day Suspension',
            final_finding='UN',
            allegation_category=category_2,
            disciplined=True
        )
        OfficerAllegationFactory(
            officer=officer_2,
            allegation=allegation_2,
            recc_outcome='Separation',
            final_outcome='Suspended Over 30 Days',
            final_finding='SU',
            allegation_category=category_2,
            disciplined=True
        )

        TRRFactory(
            id=1,
            officer=officer_3,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
            taser=True,
            firearm_used=False,
            block='17XX',
            street='Division St',
        )
        TRRFactory(
            id=2,
            officer=officer_4,
            trr_datetime=datetime(2005, 1, 1, tzinfo=pytz.utc),
            point=Point(33.3, 78.4),
            taser=False,
            firearm_used=True,
            block='34XX',
            street='Douglas Blvd',
        )

        expected_data = [
            {
                'date': '2002-01-01',
                'crid': '123',
                'category': 'Use of Force',
                'subcategory': 'Subcategory 1',
                'kind': 'CR',
                'address': '34XX Douglas Blvd',
                'to': '/complaint/123/',
                'victims': [
                    {
                        'gender': 'Male',
                        'race': 'Black',
                        'age': 35
                    }
                ],
                'coaccused': [
                    {
                        'id': 1,
                        'full_name': 'Jerome Finnigan',
                        'complaint_count': 20,
                        'sustained_count': 10,
                        'birth_year': 1980,
                        'complaint_percentile': 85.0,
                        'recommended_outcome': 'Separation',
                        'final_outcome': '30 Day Suspension',
                        'final_finding': 'Unfounded',
                        'category': 'Use of Force',
                        'disciplined': True,
                        'race': 'Asian',
                        'gender': 'Male',
                        'rank': 'Police Officer',
                        'percentile': {
                            'percentile_trr': '80.0000',
                            'percentile_allegation_civilian': '90.0000',
                            'percentile_allegation_internal': '95.0000',

                        }
                    },
                ]
            },
            {
                'date': '2003-01-01',
                'crid': '456',
                'category': 'Illegal Search',
                'subcategory': 'Subcategory 2',
                'kind': 'CR',
                'address': '34XX Douglas Blvd',
                'to': '/complaint/456/',
                'victims': [
                    {
                        'gender': 'Female',
                        'race': 'White',
                        'age': 40
                    }
                ],
                'coaccused': [
                    {
                        'id': 1,
                        'full_name': 'Jerome Finnigan',
                        'complaint_count': 20,
                        'sustained_count': 10,
                        'birth_year': 1980,
                        'complaint_percentile': 85.0,
                        'recommended_outcome': 'Separation',
                        'final_outcome': '28 Day Suspension',
                        'final_finding': 'Unfounded',
                        'category': 'Illegal Search',
                        'disciplined': True,
                        'race': 'Asian',
                        'gender': 'Male',
                        'rank': 'Police Officer',
                        'percentile': {
                            'percentile_trr': '80.0000',
                            'percentile_allegation_civilian': '90.0000',
                            'percentile_allegation_internal': '95.0000',

                        }
                    },
                    {
                        'id': 2,
                        'full_name': 'Edward May',
                        'complaint_count': 10,
                        'sustained_count': 5,
                        'birth_year': 1970,
                        'complaint_percentile': 55.0,
                        'recommended_outcome': 'Separation',
                        'final_outcome': 'Suspended Over 30 Days',
                        'final_finding': 'Sustained',
                        'category': 'Illegal Search',
                        'disciplined': True,
                        'race': 'Black',
                        'gender': 'Male',
                        'rank': 'Police Officer',
                        'percentile': {
                            'percentile_trr': '50.0000',
                            'percentile_allegation_civilian': '60.0000',
                            'percentile_allegation_internal': '65.0000',

                        }
                    },
                ],
            },
            {
                'kind': 'FORCE',
                'trr_id': 1,
                'to': '/trr/1/',
                'taser': True,
                'firearm_used': False,
                'date': '2004-01-01',
                'address': '17XX Division St',
                'officer': {
                    'id': 3,
                    'full_name': 'Jon Snow',
                    'complaint_count': 20,
                    'sustained_count': 10,
                    'birth_year': 1980,
                    'complaint_percentile': 85,
                    'race': 'Asian',
                    'gender': 'Male',
                    'rank': 'Police Officer',
                    'percentile': {
                        'percentile_trr': '80.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                    },
                },
            },
            {
                'kind': 'FORCE',
                'trr_id': 2,
                'to': '/trr/2/',
                'taser': False,
                'firearm_used': True,
                'date': '2005-01-01',
                'address': '34XX Douglas Blvd',
                'officer': {
                    'id': 4,
                    'full_name': 'David May',
                    'complaint_count': 20,
                    'sustained_count': 10,
                    'birth_year': 1980,
                    'complaint_percentile': 85,
                    'race': 'Asian',
                    'gender': 'Male',
                    'rank': 'Police Officer',
                    'percentile': {
                        'percentile_trr': '80.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                    },
                },
            },
        ]

        results = GeographyDataQuery(officers, detail=True).execute()
        results = sorted(results, key=lambda item: (item['kind'], item.get('crid', None), item.get('trr_id', None)))
        for row in results:
            if row['kind'] == 'CR':
                row['coaccused'] = sorted(row['coaccused'], key=itemgetter('id'))

        expect(len(results)).to.eq(len(expected_data))
        expect(results).to.eq(expected_data)
