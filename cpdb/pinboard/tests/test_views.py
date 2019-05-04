from datetime import datetime

from django.urls import reverse
from django.contrib.gis.geos import Point

from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect
import pytz

from pinboard.models import Pinboard
from data.factories import (
    OfficerFactory,
    AllegationFactory,
    AllegationCategoryFactory,
    OfficerAllegationFactory,
    VictimFactory,
)
from trr.factories import TRRFactory, ActionResponseFactory
from data.cache_managers import allegation_cache_manager
from pinboard.factories import PinboardFactory


class PinboardAPITestCase(APITestCase):
    def test_retrieve_pinboard(self):
        PinboardFactory(
            id='f871a13f',
            title='My Pinboard',
            description='abc',
        )

        # Current client does not own the pinboard, should clone it
        response = self.client.get(reverse('api-v2:pinboards-detail', kwargs={'pk': 'f871a13f'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        cloned_pinboard_id = response.data['id']
        expect(cloned_pinboard_id).to.ne('f871a13f')
        expect(response.data['title']).to.eq('My Pinboard')
        expect(response.data['description']).to.eq('abc')
        expect(response.data['officer_ids']).to.eq([])
        expect(response.data['crids']).to.eq([])
        expect(response.data['trr_ids']).to.eq([])

        # Now current client owns the user, successive requests should not clone pinboard
        # `id` is case-insensitive
        response = self.client.get(reverse('api-v2:pinboards-detail', kwargs={'pk': cloned_pinboard_id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': cloned_pinboard_id,
            'title': 'My Pinboard',
            'officer_ids': [],
            'crids': [],
            'trr_ids': [],
            'description': 'abc',
        })

    def test_retrieve_pinboard_not_found(self):
        PinboardFactory(
            id='d91ba25d',
            title='My Pinboard',
            description='abc',
        )

        response = self.client.get(reverse('api-v2:pinboards-detail', kwargs={'pk': 'a4f34019'}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_update_pinboard_in_the_same_session(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')
        AllegationFactory(crid='456def')

        TRRFactory(id=1, officer=OfficerFactory(id=3))
        TRRFactory(id=2, officer=OfficerFactory(id=4))

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            {
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }
        )
        pinboard_id = response.data['id']

        response = self.client.put(
            reverse('api-v2:pinboards-detail', kwargs={'pk': pinboard_id}),
            {
                'title': 'New Pinboard',
                'officer_ids': [1],
                'crids': ['456def'],
                'trr_ids': [1, 2],
                'description': 'def',
            }
        )

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': pinboard_id,
            'title': 'New Pinboard',
            'officer_ids': [1],
            'crids': ['456def'],
            'trr_ids': [1, 2],
            'description': 'def',
        })

        pinboard = Pinboard.objects.get(id=pinboard_id)
        officer_ids = set([officer.id for officer in pinboard.officers.all()])
        crids = set([allegation.crid for allegation in pinboard.allegations.all()])
        trr_ids = set([trr.id for trr in pinboard.trrs.all()])

        expect(pinboard.title).to.eq('New Pinboard')
        expect(pinboard.description).to.eq('def')
        expect(officer_ids).to.eq({1})
        expect(crids).to.eq({'456def'})
        expect(trr_ids).to.eq({1, 2})

    def test_update_pinboard_out_of_session(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')
        AllegationFactory(crid='456def')

        TRRFactory(id=1, officer=OfficerFactory(id=3))
        TRRFactory(id=2, officer=OfficerFactory(id=4))

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            {
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }
        )
        self.client.cookies.clear()

        response = self.client.put(
            reverse('api-v2:pinboards-detail', kwargs={'pk': response.data['id']}),
            {
                'title': 'New Pinboard',
                'officer_ids': [1],
                'crids': ['456def'],
                'trr_ids': [1, 2],
                'description': 'def',
            },
        )

        expect(response.status_code).to.eq(status.HTTP_403_FORBIDDEN)

    def test_create_pinboard(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')

        TRRFactory(id=1, officer=OfficerFactory(id=3))

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            {
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }
        )

        expect(response.status_code).to.eq(status.HTTP_201_CREATED)
        expect(response.data['id']).to.be.a.string()
        expect(response.data['id']).to.have.length(8)
        expect(response.data).to.eq({
            'id': response.data['id'],
            'title': 'My Pinboard',
            'officer_ids': [1, 2],
            'crids': ['123abc'],
            'trr_ids': [1],
            'description': 'abc'
        })

        expect(Pinboard.objects.count()).to.eq(1)
        pinboard = Pinboard.objects.all()

        expect(pinboard[0].title).to.eq('My Pinboard')
        expect(pinboard[0].description).to.eq('abc')
        expect(set(pinboard.values_list('officers', flat=True))).to.eq({1, 2})
        expect(set(pinboard.values_list('allegations', flat=True))).to.eq({'123abc'})
        expect(set(pinboard.values_list('trrs', flat=True))).to.eq({1})

    def test_create_pinboard_ignore_id(self):
        ignored_id = '1234ab'

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            {
                'id': ignored_id,
                'title': 'My Pinboard',
                'officer_ids': [],
                'crids': [],
                'trr_ids': [],
                'description': 'abc',
            }
        )

        expect(response.status_code).to.eq(status.HTTP_201_CREATED)
        expect(response.data['id']).to.be.a.string()
        expect(response.data['id']).to.have.length(8)
        expect(response.data['id']).to.ne(ignored_id)
        expect(response.data).to.eq({
            'id': response.data['id'],
            'title': 'My Pinboard',
            'officer_ids': [],
            'crids': [],
            'trr_ids': [],
            'description': 'abc'
        })

        expect(Pinboard.objects.filter(id=response.data['id']).exists()).to.be.true()

    def test_selected_complaints(self):
        category1 = AllegationCategoryFactory(
            category='Use Of Force',
            allegation_name='Miscellaneous',
        )
        category2 = AllegationCategoryFactory(
            category='Verbal Abuse',
            allegation_name='Miscellaneous',
        )

        allegation1 = AllegationFactory(
            crid='1000001',
            incident_date=datetime(2010, 1, 1, tzinfo=pytz.utc),
            point=Point(1.0, 1.0),
        )
        allegation2 = AllegationFactory(
            crid='1000002',
            incident_date=datetime(2011, 1, 1, tzinfo=pytz.utc),
            point=Point(2.0, 2.0),
        )
        allegation3 = AllegationFactory(
            crid='1000003',
            incident_date=datetime(2012, 1, 1, tzinfo=pytz.utc),
            point=Point(3.0, 3.0),
        )

        OfficerAllegationFactory(allegation=allegation1, allegation_category=category1)
        OfficerAllegationFactory(allegation=allegation2, allegation_category=category2)
        OfficerAllegationFactory(allegation=allegation3, allegation_category=category2)

        allegation_cache_manager.cache_data()

        allegation1.refresh_from_db()
        allegation2.refresh_from_db()
        allegation3.refresh_from_db()

        pinboard = PinboardFactory(allegations=(allegation1, allegation2))

        response = self.client.get(reverse('api-v2:pinboards-complaints', kwargs={'pk': pinboard.id}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'crid': '1000001',
                'incident_date': '2010-01-01',
                'point': {'lon': 1.0, 'lat': 1.0},
                'most_common_category': 'Use Of Force',
            },
            {
                'crid': '1000002',
                'incident_date': '2011-01-01',
                'point': {'lon': 2.0, 'lat': 2.0},
                'most_common_category': 'Verbal Abuse',
            }
        ])

    def test_selected_officers(self):
        officer1 = OfficerFactory(
            id=1, first_name='Daryl', last_name='Mack',
            trr_percentile=12.0000,
            civilian_allegation_percentile=98.4344,
            internal_allegation_percentile=99.7840,
            complaint_percentile=99.3450,
            race='White', gender='M', birth_year=1975,
            rank='Police Officer'
        )
        officer2 = OfficerFactory(
            id=2,
            first_name='Ronald', last_name='Watts',
            trr_percentile=0.0000,
            civilian_allegation_percentile=98.4344,
            internal_allegation_percentile=99.7840,
            complaint_percentile=99.5000,
            race='White', gender='M', birth_year=1975,
            rank='Detective'
        )
        OfficerFactory(id=3)

        pinboard = PinboardFactory(officers=(officer1, officer2))

        response = self.client.get(reverse('api-v2:pinboards-officers', kwargs={'pk': pinboard.id}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'id': 1,
                'full_name': 'Daryl Mack',
                'complaint_count': 0,
                'sustained_count': 0,
                'birth_year': 1975,
                'complaint_percentile': 99.3450,
                'race': 'White',
                'gender': 'Male',
                'rank': 'Police Officer',
                'percentile': {
                    'percentile_trr': '12.0000',
                    'percentile_allegation': '99.3450',
                    'percentile_allegation_civilian': '98.4344',
                    'percentile_allegation_internal': '99.7840',
                    'year': 2016,
                    'id': 1,
                }
            },
            {
                'id': 2,
                'full_name': 'Ronald Watts',
                'complaint_count': 0,
                'sustained_count': 0,
                'birth_year': 1975,
                'complaint_percentile': 99.5000,
                'race': 'White',
                'gender': 'Male',
                'rank': 'Detective',
                'percentile': {
                    'percentile_trr': '0.0000',
                    'percentile_allegation': '99.5000',
                    'percentile_allegation_civilian': '98.4344',
                    'percentile_allegation_internal': '99.7840',
                    'year': 2016,
                    'id': 2,
                }
            }
        ])

    def test_selected_trrs(self):
        trr1 = TRRFactory(
            id=1,
            trr_datetime=datetime(2012, 1, 1, tzinfo=pytz.utc),
            point=Point(1.0, 1.0),
        )
        trr2 = TRRFactory(
            id=2,
            trr_datetime=datetime(2013, 1, 1, tzinfo=pytz.utc),
            point=None,
        )
        TRRFactory(id=3)

        ActionResponseFactory(trr=trr1, force_type='Physical Force - Stunning', action_sub_category='1')
        ActionResponseFactory(trr=trr1, force_type='Impact Weapon', action_sub_category='2')

        pinboard = PinboardFactory(trrs=(trr1, trr2))

        response = self.client.get(reverse('api-v2:pinboards-trrs', kwargs={'pk': pinboard.id}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'id': 1,
                'trr_datetime': '2012-01-01',
                'category': 'Impact Weapon',
                'point': {'lon': 1.0, 'lat': 1.0},
            },
            {
                'id': 2,
                'trr_datetime': '2013-01-01',
                'category': 'Unknown',
                'point': None,
            }
        ])

    def test_social_graph(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')
        officer_4 = OfficerFactory(id=8565, first_name='William', last_name='People')

        allegation_1 = AllegationFactory(
            crid='123',
            is_officer_complaint=False,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc)
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=True,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc)
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc)
        )
        trr_1 = TRRFactory(
            id=1,
            officer=officer_4,
            trr_datetime=datetime(2008, 12, 31, tzinfo=pytz.utc)
        )

        OfficerAllegationFactory(id=1, officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_2, allegation=allegation_1)
        OfficerAllegationFactory(id=3, officer=officer_1, allegation=allegation_2)
        OfficerAllegationFactory(id=4, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=5, officer=officer_1, allegation=allegation_3)
        OfficerAllegationFactory(id=6, officer=officer_2, allegation=allegation_3)
        OfficerAllegationFactory(id=7, officer=officer_3, allegation=allegation_3)

        pinboard = PinboardFactory(
            title='My Pinboard',
            description='abc',
        )

        pinboard.officers.set([officer_1, officer_2])
        pinboard.allegations.set([allegation_3])
        pinboard.trrs.set([trr_1])

        expected_data = {
            'officers': [
                {'full_name': 'Edward May', 'id': 8563},
                {'full_name': 'Jerome Finnigan', 'id': 8562},
                {'full_name': 'Joe Parker', 'id': 8564},
                {'full_name': 'William People', 'id': 8565},
            ],
            'coaccused_data': [
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': datetime(2005, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 1
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': datetime(2006, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8563,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 3
                },
                {
                    'officer_id_1': 8562,
                    'officer_id_2': 8564,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 1
                },
                {
                    'officer_id_1': 8563,
                    'officer_id_2': 8564,
                    'incident_date': datetime(2007, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 1
                },
            ],
            'list_event': ['2005-12-31 00:00:00+00:00', '2006-12-31 00:00:00+00:00', '2007-12-31 00:00:00+00:00']
        }

        response = self.client.get(reverse('api-v2:pinboards-social-graph', kwargs={'pk': pinboard.id}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)

    def test_geographic_data(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)

        category_1 = AllegationCategoryFactory(category='Use of Force', allegation_name='Subcategory 1')
        category_2 = AllegationCategoryFactory(category='Illegal Search', allegation_name='Subcategory 2')
        allegation_1 = AllegationFactory(
            crid=123,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_1,
            coaccused_count=15,
            point=Point(-35.5, 68.9),
        )
        allegation_2 = AllegationFactory(
            crid=456,
            incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc),
            most_common_category=category_2,
            coaccused_count=20,
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

        pinboard = PinboardFactory(
            title='My Pinboard',
            description='abc',
        )

        pinboard.officers.set([officer_3, officer_4])
        pinboard.allegations.set([allegation_1, allegation_2])

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

        response = self.client.get(reverse('api-v2:pinboards-geographic-data', kwargs={'pk': pinboard.id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        for data in expected_data:
            expect(response.data).to.contain(data)

    def test_latest_retrieved_pinboard(self):
        # No previous pinboard, data returned should be null
        response = self.client.get(reverse('api-v2:pinboards-latest-retrieved-pinboard'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({})

        # Create a pinboard in current session
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')

        TRRFactory(id=1, officer=OfficerFactory(id=3))

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            {
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }
        )
        pinboard_id = response.data['id']

        # Latest retrieved pinboard is now the above one
        response = self.client.get(reverse('api-v2:pinboards-latest-retrieved-pinboard'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': pinboard_id,
            'title': 'My Pinboard',
            'officer_ids': [1, 2],
            'crids': ['123abc'],
            'trr_ids': [1],
            'description': 'abc',
        })
