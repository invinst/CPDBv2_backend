from datetime import datetime, date
from urllib.parse import urlencode
from operator import itemgetter
import json

from django.contrib.gis.geos import Point
from django.urls import reverse

import pytz
from mock import patch, Mock, PropertyMock
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from robber import expect
from freezegun import freeze_time

from authentication.factories import AdminUserFactory
from data.cache_managers import allegation_cache_manager
from data.factories import (
    OfficerFactory,
    AllegationFactory,
    AllegationCategoryFactory,
    OfficerAllegationFactory,
    AttachmentFileFactory,
    InvestigatorAllegationFactory,
    PoliceWitnessFactory,
    PoliceUnitFactory,
    OfficerBadgeNumberFactory,
    OfficerHistoryFactory,
    VictimFactory,
)
from pinboard.factories import PinboardFactory, ExamplePinboardFactory
from pinboard.models import Pinboard
from trr.factories import TRRFactory, ActionResponseFactory


@patch('data.constants.MAX_VISUAL_TOKEN_YEAR', 2016)
class PinboardDesktopViewSetTestCase(APITestCase):
    def test_retrieve_pinboard(self):
        example_pinboard_1 = PinboardFactory(
            id='eeee1111',
            title='Example pinboard 1',
            description='Example pinboard 1',
        )
        example_pinboard_2 = PinboardFactory(
            id='eeee2222',
            title='Example pinboard 2',
            description='Example pinboard 2',
        )
        ExamplePinboardFactory(pinboard=example_pinboard_1)
        ExamplePinboardFactory(pinboard=example_pinboard_2)

        officer_1 = OfficerFactory(id=11)
        officer_2 = OfficerFactory(id=22)
        allegation_1 = AllegationFactory(crid='abc123')
        allegation_2 = AllegationFactory(crid='abc456')
        trr_1 = TRRFactory(id=33)
        trr_2 = TRRFactory(id=44)

        pinboard = PinboardFactory(
            id='f871a13f',
            title='My Pinboard',
            description='abc',
            officers=[officer_1, officer_2],
            allegations=[allegation_1, allegation_2],
            trrs=[trr_1, trr_2],
        )

        # Current client does not own the pinboard, should clone it
        response = self.client.get(reverse('api-v2:pinboards-detail', kwargs={'pk': 'f871a13f'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        cloned_pinboard_id = response.data['id']
        expect(cloned_pinboard_id).to.ne('f871a13f')
        expect(response.data['title']).to.eq('My Pinboard')
        expect(response.data['description']).to.eq('abc')
        expect(set(response.data['officer_ids'])).to.eq({11, 22})
        expect(set(response.data['crids'])).to.eq({'abc123', 'abc456'})
        expect(set(response.data['trr_ids'])).to.eq({33, 44})

        cloned_pinboard = Pinboard.objects.get(id=cloned_pinboard_id)
        expect(cloned_pinboard.source_pinboard).to.eq(pinboard)
        expect(cloned_pinboard.title).to.eq('My Pinboard')
        expect(cloned_pinboard.description).to.eq('abc')
        expect(set(cloned_pinboard.officer_ids)).to.eq({11, 22})
        expect(set(cloned_pinboard.crids)).to.eq({'abc123', 'abc456'})
        expect(set(cloned_pinboard.trr_ids)).to.eq({33, 44})

        # Now current client owns the user, successive requests should not clone pinboard
        # `id` is case-insensitive
        response = self.client.get(reverse('api-v2:pinboards-detail', kwargs={'pk': cloned_pinboard_id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data['id']).to.eq(cloned_pinboard_id)
        expect(response.data['title']).to.eq('My Pinboard')
        expect(set(response.data['officer_ids'])).to.eq({11, 22})
        expect(set(response.data['crids'])).to.eq({'abc123', 'abc456'})
        expect(set(response.data['trr_ids'])).to.eq({33, 44})
        expect(response.data['description']).to.eq('abc')
        expect(response.data).not_to.contain('example_pinboards')

    def test_retrieve_empty_pinboard(self):
        example_pinboard_1 = PinboardFactory(
            id='eeee1111',
            title='Example pinboard 1',
            description='Example pinboard 1',
        )
        example_pinboard_2 = PinboardFactory(
            id='eeee2222',
            title='Example pinboard 2',
            description='Example pinboard 2',
        )
        ExamplePinboardFactory(pinboard=example_pinboard_1)
        ExamplePinboardFactory(pinboard=example_pinboard_2)

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

        expect(response.data['id']).to.eq(cloned_pinboard_id)
        expect(response.data['title']).to.eq('My Pinboard')
        expect(response.data['officer_ids']).to.eq([])
        expect(response.data['crids']).to.eq([])
        expect(response.data['trr_ids']).to.eq([])
        expect(response.data['description']).to.eq('abc')

        expect(response.data['example_pinboards']).to.contain({
            'id': 'eeee1111',
            'title': 'Example pinboard 1',
            'description': 'Example pinboard 1',
        }, {
            'id': 'eeee2222',
            'title': 'Example pinboard 2',
            'description': 'Example pinboard 2',
        })

    def test_retrieve_pinboard_not_found(self):
        PinboardFactory(
            id='d91ba25d',
            title='My Pinboard',
            description='abc',
        )
        expect(Pinboard.objects.count()).to.eq(1)

        response = self.client.get(reverse('api-v2:pinboards-detail', kwargs={'pk': 'a4f34019'}))

        expect(Pinboard.objects.count()).to.eq(2)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['id']).to.ne('d91ba25d')
        expect(response.data['title']).to.eq('')
        expect(response.data['officer_ids']).to.eq([])
        expect(response.data['crids']).to.eq([])
        expect(response.data['trr_ids']).to.eq([])
        expect(response.data['description']).to.eq('')

    def test_update_pinboard_in_the_same_session(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')
        AllegationFactory(crid='456def')

        TRRFactory(id=1, officer=OfficerFactory(id=3))
        TRRFactory(id=2, officer=OfficerFactory(id=4))

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json'
        )
        pinboard_id = response.data['id']

        response = self.client.put(
            reverse('api-v2:pinboards-detail', kwargs={'pk': pinboard_id}),
            json.dumps({
                'title': 'New Pinboard',
                'officer_ids': [1],
                'crids': ['456def'],
                'trr_ids': [1, 2],
                'description': 'def',
            }),
            content_type='application/json'
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

    def test_update_pinboard_in_the_same_session_with_source_id(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)

        allegation_1 = AllegationFactory(crid='123abc')
        AllegationFactory(crid='456def')

        trr_1 = TRRFactory(id=1, officer=OfficerFactory(id=3))
        TRRFactory(id=2, officer=OfficerFactory(id=4))

        source_pinboard = PinboardFactory(
            id='eeee1111',
            title='Example pinboard 1',
            description='Example pinboard 1',
        )
        source_pinboard.officers.set([officer_1, officer_2])
        source_pinboard.allegations.set([allegation_1])
        source_pinboard.trrs.set([trr_1])

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            json.dumps({
                'title': '',
                'officer_ids': [],
                'crids': [],
                'trr_ids': [],
                'description': '',
            }),
            content_type='application/json'
        )
        pinboard_id = response.data['id']

        response = self.client.put(
            reverse('api-v2:pinboards-detail', kwargs={'pk': pinboard_id}),
            json.dumps({
                'source_pinboard_id': 'eeee1111',
            }),
            content_type='application/json'
        )

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': pinboard_id,
            'title': 'Example pinboard 1',
            'officer_ids': [1, 2],
            'crids': ['123abc'],
            'trr_ids': [1],
            'description': 'Example pinboard 1',
        })

        pinboard = Pinboard.objects.get(id=pinboard_id)
        officer_ids = set([officer.id for officer in pinboard.officers.all()])
        crids = set([allegation.crid for allegation in pinboard.allegations.all()])
        trr_ids = set([trr.id for trr in pinboard.trrs.all()])

        expect(pinboard.title).to.eq('Example pinboard 1')
        expect(pinboard.description).to.eq('Example pinboard 1')
        expect(officer_ids).to.eq({1, 2})
        expect(crids).to.eq({'123abc'})
        expect(trr_ids).to.eq({1})

    def test_update_when_have_multiple_pinboards_in_session(self):
        owned_pinboards = []

        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')
        AllegationFactory(crid='456def')

        TRRFactory(id=1, officer=OfficerFactory(id=3))
        TRRFactory(id=2, officer=OfficerFactory(id=4))

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json'
        )

        owned_pinboards.append(response.data['id'])

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json'
        )

        owned_pinboards.append(response.data['id'])

        # Try updating the old pinboardresponse = self.client.put(
        response = self.client.put(
            reverse('api-v2:pinboards-detail', kwargs={'pk': owned_pinboards[0]}),
            json.dumps({
                'title': 'New Pinboard',
                'officer_ids': [1],
                'crids': ['456def'],
                'trr_ids': [1, 2],
                'description': 'def',
            }),
            content_type='application/json'
        )

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': owned_pinboards[0],
            'title': 'New Pinboard',
            'officer_ids': [1],
            'crids': ['456def'],
            'trr_ids': [1, 2],
            'description': 'def',
        })

    def test_update_pinboard_out_of_session(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')
        AllegationFactory(crid='456def')

        TRRFactory(id=1, officer=OfficerFactory(id=3))
        TRRFactory(id=2, officer=OfficerFactory(id=4))

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json'
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
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json'
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
        example_pinboard_1 = PinboardFactory(
            id='eeee1111',
            title='Example pinboard 1',
            description='Example pinboard 1',
        )
        example_pinboard_2 = PinboardFactory(
            id='eeee2222',
            title='Example pinboard 2',
            description='Example pinboard 2',
        )
        ExamplePinboardFactory(pinboard=example_pinboard_1)
        ExamplePinboardFactory(pinboard=example_pinboard_2)

        ignored_id = '1234ab'

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            json.dumps({
                'id': ignored_id,
                'title': 'My Pinboard',
                'officer_ids': [],
                'crids': [],
                'trr_ids': [],
                'description': 'abc',
            }),
            content_type='application/json'
        )

        expect(response.status_code).to.eq(status.HTTP_201_CREATED)
        expect(response.data['id']).to.be.a.string()
        expect(response.data['id']).to.have.length(8)
        expect(response.data['id']).to.ne(ignored_id)

        expect(response.data['id']).to.eq(response.data['id'])
        expect(response.data['title']).to.eq('My Pinboard')
        expect(response.data['officer_ids']).to.eq([])
        expect(response.data['crids']).to.eq([])
        expect(response.data['trr_ids']).to.eq([])
        expect(response.data['description']).to.eq('abc')

        expect(response.data['example_pinboards']).to.contain({
            'id': 'eeee1111',
            'title': 'Example pinboard 1',
            'description': 'Example pinboard 1',
        }, {
            'id': 'eeee2222',
            'title': 'Example pinboard 2',
            'description': 'Example pinboard 2',
        })

        expect(Pinboard.objects.filter(id=response.data['id']).exists()).to.be.true()

    def test_create_pinboard_not_found_pinned_item_ids(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')

        TRRFactory(id=1, officer=OfficerFactory(id=3))

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2, 3, 4, 5],
                'crids': ['789xyz', 'zyx123', '123abc'],
                'trr_ids': [0, 1, 3, 4],
                'description': 'abc',
            }),
            content_type='application/json'
        )

        expect(response.status_code).to.eq(status.HTTP_201_CREATED)
        expect(response.data['id']).to.be.a.string()
        expect(response.data['id']).to.have.length(8)
        expect(response.data).to.eq({
            'id': response.data['id'],
            'title': 'My Pinboard',
            'officer_ids': [1, 2, 3],
            'crids': ['123abc'],
            'trr_ids': [1],
            'description': 'abc',
            'not_found_items': {
                'officer_ids': [4, 5],
                'crids': ['789xyz', 'zyx123'],
                'trr_ids': [0, 3, 4],
            }
        })

        expect(Pinboard.objects.count()).to.eq(1)
        pinboard = Pinboard.objects.all()

        expect(pinboard[0].title).to.eq('My Pinboard')
        expect(pinboard[0].description).to.eq('abc')
        expect(set(pinboard.values_list('officers', flat=True))).to.eq({1, 2, 3})
        expect(set(pinboard.values_list('allegations', flat=True))).to.eq({'123abc'})
        expect(set(pinboard.values_list('trrs', flat=True))).to.eq({1})

    def test_create_pinboard_with_source_id(self):
        officer_1 = OfficerFactory(id=111)
        officer_2 = OfficerFactory(id=222)
        allegation = AllegationFactory(crid='1111')
        trr_1 = TRRFactory(id=3)
        trr_2 = TRRFactory(id=4)

        pinboard = PinboardFactory(
            id='1234abcd',
            title='Duplicate Pinboard Title',
            description='Duplicate Pinboard Description',
            officers=[officer_1, officer_2],
            allegations=[allegation],
            trrs=[trr_1, trr_2],
        )

        expect(Pinboard.objects.count()).to.eq(1)

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            {
                'source_pinboard_id': '1234abcd',
            }
        )

        expect(Pinboard.objects.count()).to.eq(2)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['id']).to.be.a.string()
        expect(response.data['id']).to.have.length(8)
        expect(response.data).to.eq({
            'id': response.data['id'],
            'title': 'Duplicate Pinboard Title copy',
            'officer_ids': [111, 222],
            'crids': ['1111'],
            'trr_ids': [3, 4],
            'description': 'Duplicate Pinboard Description'
        })

        duplicated_pinboard = Pinboard.objects.get(id=response.data['id'])

        expect(duplicated_pinboard.source_pinboard).to.eq(pinboard)
        expect(duplicated_pinboard.title).to.eq('Duplicate Pinboard Title copy')
        expect(duplicated_pinboard.description).to.eq('Duplicate Pinboard Description')
        expect(set(duplicated_pinboard.officer_ids)).to.eq({111, 222})
        expect(set(duplicated_pinboard.crids)).to.eq({'1111'})
        expect(set(duplicated_pinboard.trr_ids)).to.eq({3, 4})

    def test_selected_complaints(self):
        category1 = AllegationCategoryFactory(
            category='Use Of Force',
            allegation_name='Miscellaneous',
        )
        allegation1 = AllegationFactory(
            crid='123',
            old_complaint_address='16XX N TALMAN AVE, CHICAGO IL',
            most_common_category=category1,
            point=Point(-35.5, 68.9),
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
        )
        coaccused1 = OfficerFactory(
            id=1,
            first_name='Jesse',
            last_name='Pinkman',
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
            officer=coaccused1,
            allegation=allegation1,
            recc_outcome='11 Day Suspension',
            final_outcome='Separation',
            final_finding='SU',
            allegation_category=category1,
            disciplined=True,
        )
        VictimFactory(
            allegation=allegation1,
            gender='F',
            race='White',
            age=40,
        )

        category2 = AllegationCategoryFactory(
            category='Verbal Abuse',
            allegation_name='Miscellaneous',
        )
        allegation2 = AllegationFactory(
            crid='124',
            old_complaint_address='17XX N TALMAN AVE, CHICAGO IL',
            most_common_category=category1,
            point=Point(-35.5, 68.9),
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
        )
        coaccused2 = OfficerFactory(
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
            officer=coaccused2,
            allegation=allegation2,
            recc_outcome='10 Day Suspension',
            final_outcome='Separation',
            final_finding='SU',
            allegation_category=category2,
            disciplined=True,
        )
        VictimFactory(
            allegation=allegation2,
            gender='M',
            race='White',
            age=40,
        )

        allegation_cache_manager.cache_data()

        allegation1.refresh_from_db()
        allegation2.refresh_from_db()

        pinboard = PinboardFactory(allegations=(allegation1, allegation2))

        response = self.client.get(reverse('api-v2:pinboards-complaints', kwargs={'pk': pinboard.id}))

        results = sorted(response.data, key=itemgetter('crid'))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(results).to.eq([
            {
                'crid': '123',
                'address': '16XX N TALMAN AVE, CHICAGO IL',
                'category': 'Use Of Force',
                'incident_date': '2002-01-01',
                'victims': [{
                    'gender': 'Female',
                    'race': 'White',
                    'age': 40,
                }],
                'point': {'lon': -35.5, 'lat': 68.9},
                'to': '/complaint/123/',
                'sub_category': 'Miscellaneous',
                'coaccused': [{
                    'id': 1,
                    'full_name': 'Jesse Pinkman',
                    'complaint_count': 6,
                    'sustained_count': 5,
                    'birth_year': 1940,
                    'recommended_outcome': '11 Day Suspension',
                    'final_outcome': 'Separation',
                    'final_finding': 'Sustained',
                    'category': 'Use Of Force',
                    'disciplined': True,
                    'race': 'White',
                    'gender': 'Male',
                    'rank': 'Sergeant of Police',
                    'percentile_allegation': '0.0000',
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000',
                }],
            },
            {
                'crid': '124',
                'address': '17XX N TALMAN AVE, CHICAGO IL',
                'category': 'Verbal Abuse',
                'incident_date': '2002-01-01',
                'victims': [{
                    'gender': 'Male',
                    'race': 'White',
                    'age': 40,
                }],
                'point': {'lon': -35.5, 'lat': 68.9},
                'to': '/complaint/124/',
                'sub_category': 'Miscellaneous',
                'coaccused': [{
                    'id': 2,
                    'full_name': 'Walter White',
                    'complaint_count': 6,
                    'sustained_count': 5,
                    'birth_year': 1940,
                    'recommended_outcome': '10 Day Suspension',
                    'final_outcome': 'Separation',
                    'final_finding': 'Sustained',
                    'category': 'Verbal Abuse',
                    'disciplined': True,
                    'race': 'White',
                    'gender': 'Male',
                    'rank': 'Sergeant of Police',
                    'percentile_allegation': '0.0000',
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000',
                }],
            }
        ])

    def test_selected_complaints_pinboard_not_exist(self):
        response = self.client.get(reverse('api-v2:pinboards-complaints', kwargs={'pk': '1'}))
        expect(response.data).to.eq([])

    @patch(
        'data.models.Officer.coaccusals',
        new_callable=PropertyMock,
        return_value=[Mock(id=789, coaccusal_count=10)]
    )
    def test_selected_officers(self, _):
        unit = PoliceUnitFactory(
            id=4,
            unit_name='004',
            description='District 004',
        )
        old_unit = PoliceUnitFactory(
            id=5,
            unit_name='005',
            description='District 005',
        )

        officer = OfficerFactory(
            id=123,
            tags=['tag1', 'tag2'],
            first_name='Michael',
            last_name='Flynn',
            last_unit=unit,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            active='Yes',
            rank='Sergeant',
            race='Black',
            gender='F',
            current_badge='456',
            birth_year=1950,
            current_salary=10000,
            allegation_count=20,
            complaint_percentile='99.9900',
            honorable_mention_count=3,
            sustained_count=4,
            unsustained_count=5,
            discipline_count=6,
            civilian_compliment_count=2,
            trr_count=7,
            major_award_count=8,
            honorable_mention_percentile='88.8800',
            has_unique_name=True,
            civilian_allegation_percentile=None,
            internal_allegation_percentile=None,
            trr_percentile=None,
        )

        OfficerBadgeNumberFactory(
            officer=officer,
            current=False,
            star='789'
        )
        OfficerBadgeNumberFactory(
            officer=officer,
            current=True,
            star='456'
        )

        OfficerHistoryFactory(officer=officer, unit=old_unit, effective_date=date(2002, 1, 2))
        OfficerHistoryFactory(officer=officer, unit=unit, effective_date=date(2004, 1, 2))

        OfficerFactory(id=2)

        pinboard = PinboardFactory(officers=(officer,))

        response = self.client.get(reverse('api-v2:pinboards-officers', kwargs={'pk': pinboard.id}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([{
            'id': 123,
            'full_name': 'Michael Flynn',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/123/michael-flynn/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'Sergeant',
            'percentile_allegation': '99.9900',
            'allegation_count': 20,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004',
            }
        }])

    def test_selected_trrs(self):
        officer = OfficerFactory(
            id=1, first_name='Daryl',
            last_name='Mack',
            trr_percentile=12.0000,
            civilian_allegation_percentile=98.4344,
            internal_allegation_percentile=99.7840,
            complaint_percentile=99.3450,
            race='White', gender='M', birth_year=1975,
            rank='Police Officer'
        )

        trr1 = TRRFactory(
            id=1,
            trr_datetime=datetime(2012, 1, 1, tzinfo=pytz.utc),
            point=Point(1.0, 1.0),
            taser=False,
            firearm_used=False,
            block='14XX',
            street='CHICAGO IL 60636',
            officer=officer
        )
        trr2 = TRRFactory(
            id=2,
            trr_datetime=datetime(2013, 1, 1, tzinfo=pytz.utc),
            point=None,
            taser=True,
            firearm_used=True,
            block='15xx',
            street='CHICAGO IL 60636',
            officer=officer
        )
        TRRFactory(id=3)

        ActionResponseFactory(trr=trr1, force_type='Physical Force - Stunning', action_sub_category='1')
        ActionResponseFactory(trr=trr1, force_type='Impact Weapon', action_sub_category='2')

        pinboard = PinboardFactory(trrs=(trr1, trr2))

        response = self.client.get(reverse('api-v2:pinboards-trrs', kwargs={'pk': pinboard.id}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expected_results = [
            {
                'id': 1,
                'trr_datetime': '2012-01-01',
                'category': 'Impact Weapon',
                'point': {'lon': 1.0, 'lat': 1.0},
                'to': '/trr/1/',
                'taser': False,
                'firearm_used': False,
                'address': '14XX CHICAGO IL 60636',
                'officer': {
                    'id': 1,
                    'full_name': 'Daryl Mack',
                    'complaint_count': 0,
                    'sustained_count': 0,
                    'birth_year': 1975,
                    'race': 'White',
                    'gender': 'Male',
                    'rank': 'Police Officer',
                    'percentile_allegation': '99.3450',
                    'percentile_allegation_civilian': '98.4344',
                    'percentile_allegation_internal': '99.7840',
                    'percentile_trr': '12.0000',
                }
            },
            {
                'id': 2,
                'trr_datetime': '2013-01-01',
                'category': 'Unknown',
                'to': '/trr/2/',
                'taser': True,
                'firearm_used': True,
                'address': '15xx CHICAGO IL 60636',
                'officer': {
                    'id': 1,
                    'full_name': 'Daryl Mack',
                    'complaint_count': 0,
                    'sustained_count': 0,
                    'birth_year': 1975,
                    'race': 'White',
                    'gender': 'Male',
                    'rank': 'Police Officer',
                    'percentile_allegation': '99.3450',
                    'percentile_allegation_civilian': '98.4344',
                    'percentile_allegation_internal': '99.7840',
                    'percentile_trr': '12.0000',
                }
            }
        ]
        expect(response.data).to.eq(expected_results)

    def test_relevant_documents(self):
        pinned_officer_1 = OfficerFactory(
            id=1,
            rank='Police Officer',
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=10,
            trr_percentile='99.99',
            complaint_percentile='88.88',
            civilian_allegation_percentile='77.77',
            internal_allegation_percentile='66.66',
        )
        pinned_officer_2 = OfficerFactory(
            id=2,
            rank='Detective',
            first_name='Edward',
            last_name='May',
            allegation_count=3,
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44'
        )
        pinned_officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(
            id=4,
            rank='Senior Police Officer',
            first_name='Raymond',
            last_name='Piwinicki',
            complaint_percentile=None,
            allegation_count=20,
        )
        relevant_allegation_1 = AllegationFactory(
            crid='1',
            incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc),
            most_common_category=AllegationCategoryFactory(category='Operation/Personnel Violations'),
            point=Point([0.01, 0.02]),
        )
        relevant_allegation_2 = AllegationFactory(
            crid='2',
            add1='LTK street',
            incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc),
            point=None,
        )
        VictimFactory(allegation=relevant_allegation_2, gender='F', age=65)
        VictimFactory(allegation=relevant_allegation_2, gender='M', age=54)
        not_relevant_allegation = AllegationFactory(crid='not relevant')
        AttachmentFileFactory(
            id=1,
            file_type='document',
            title='relevant document 1',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            url='http://cr-1-document.com/',
        )
        AttachmentFileFactory(
            id=2,
            file_type='document',
            title='relevant document 2',
            allegation=relevant_allegation_2,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-2-CR-p1-normal.gif",
            url='http://cr-2-document.com/',
        )
        AttachmentFileFactory(
            id=998, file_type='document', title='relevant but not show', allegation=relevant_allegation_1, show=False
        )
        AttachmentFileFactory(
            id=999, file_type='document', title='not relevant', allegation=not_relevant_allegation, show=True
        )

        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2, pinned_officer_3])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=pinned_officer_2, allegation=relevant_allegation_2)
        OfficerAllegationFactory(officer=officer_4, allegation=relevant_allegation_2)

        response = self.client.get(reverse('api-v2:pinboards-relevant-documents', kwargs={'pk': '66ef1560'}))

        expected_results = [{
            'id': 2,
            'preview_image_url': "https://assets.documentcloud.org/CRID-2-CR-p1-normal.gif",
            'url': 'http://cr-2-document.com/',
            'allegation': {
                'crid': '2',
                'category': 'Unknown',
                'incident_date': '2002-02-22',
                'coaccused': [
                    {
                        'id': 4,
                        'rank': 'Senior Police Officer',
                        'full_name': 'Raymond Piwinicki',
                        'allegation_count': 20,
                    },
                    {
                        'id': 2,
                        'rank': 'Detective',
                        'full_name': 'Edward May',
                        'allegation_count': 3,
                        'percentile_allegation': '22.2200',
                        'percentile_allegation_civilian': '33.3300',
                        'percentile_allegation_internal': '44.4400',
                        'percentile_trr': '11.1100',
                    },
                ],
                'address': 'LTK street',
                'victims': [
                    {
                        'gender': 'Female',
                        'race': 'Black',
                        'age': 65
                    },
                    {
                        'gender': 'Male',
                        'race': 'Black',
                        'age': 54
                    }
                ],
                'to': '/complaint/2/',
                'sub_category': 'Unknown',
            }
        }, {
            'id': 1,
            'preview_image_url': "https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            'url': 'http://cr-1-document.com/',
            'allegation': {
                'crid': '1',
                'address': '',
                'category': 'Operation/Personnel Violations',
                'incident_date': '2002-02-21',
                'coaccused': [{
                    'id': 1,
                    'rank': 'Police Officer',
                    'full_name': 'Jerome Finnigan',
                    'allegation_count': 10,
                    'percentile_allegation': '88.8800',
                    'percentile_allegation_civilian': '77.7700',
                    'percentile_allegation_internal': '66.6600',
                    'percentile_trr': '99.9900',
                }],
                'sub_category': '',
                'victims': [],
                'to': '/complaint/1/',
                'point': {'lon': 0.01, 'lat': 0.02},
            }
        }]

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['results'][0]).to.eq(expected_results[0])
        expect(response.data['results'][1]).to.eq(expected_results[1])
        expect(response.data['results']).to.eq(expected_results)
        expect(response.data['count']).to.eq(2)
        expect(response.data['previous']).to.be.none()
        expect(response.data['next']).to.be.none()

    def test_relevant_documents_pagination(self):
        pinned_officer_1 = OfficerFactory(
            id=1,
            rank='Police Officer',
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=10,
            trr_percentile='99.99',
            complaint_percentile='88.88',
            civilian_allegation_percentile='77.77',
            internal_allegation_percentile='66.66'
        )

        relevant_allegation_1 = AllegationFactory(
            crid='1',
            incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc),
            most_common_category=AllegationCategoryFactory(category='Operation/Personnel Violations')
        )

        AttachmentFileFactory(
            id=1,
            file_type='document',
            title='relevant document 1',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            url='http://cr-1-document.com/',
        )
        AttachmentFileFactory(
            id=2,
            file_type='document',
            title='relevant document 2',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-2-CR-p1-normal.gif",
            url='http://cr-2-document.com/',
        )
        AttachmentFileFactory(
            id=3,
            file_type='document',
            title='relevant document 3',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-3-CR-p1-normal.gif",
            url='http://cr-3-document.com/',
        )
        AttachmentFileFactory(
            id=4,
            file_type='document',
            title='relevant document 4',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-4-CR-p1-normal.gif",
            url='http://cr-1-document.com/',
        )
        AttachmentFileFactory(
            id=5,
            file_type='document',
            title='relevant document 5',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-5-CR-p1-normal.gif",
            url='http://cr-5-document.com/',
        )

        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=relevant_allegation_1)

        base_url = reverse('api-v2:pinboards-relevant-documents', kwargs={'pk': '66ef1560'})
        first_response = self.client.get(f"{base_url}?{urlencode({'limit': 2})}")
        expect(first_response.status_code).to.eq(status.HTTP_200_OK)
        expect(first_response.data['results']).to.have.length(2)
        expect(first_response.data['count']).to.eq(5)
        expect(first_response.data['previous']).to.be.none()
        expect(first_response.data['next']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-documents/?limit=2&offset=2'
        )

        second_response = self.client.get(f"{base_url}?{urlencode({'limit': 2, 'offset': 2})}")
        expect(second_response.status_code).to.eq(status.HTTP_200_OK)
        expect(second_response.data['results']).to.have.length(2)
        expect(second_response.data['count']).to.eq(5)
        expect(second_response.data['previous']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-documents/?limit=2'
        )
        expect(second_response.data['next']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-documents/?limit=2&offset=4'
        )

        last_response = self.client.get(f"{base_url}?{urlencode({'limit': 2, 'offset': 4})}")
        expect(last_response.status_code).to.eq(status.HTTP_200_OK)
        expect(last_response.data['results']).to.have.length(1)
        expect(last_response.data['count']).to.eq(5)
        expect(last_response.data['previous']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-documents/?limit=2&offset=2'
        )
        expect(last_response.data['next']).to.be.none()

    def test_relevant_coaccusals(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_allegation_1 = AllegationFactory(crid='1')
        pinned_allegation_2 = AllegationFactory(crid='2')
        pinned_allegation_3 = AllegationFactory(crid='3')
        unit = PoliceUnitFactory(
            id=4,
            unit_name='004',
            description='District 004'
        )

        temp_officer = OfficerFactory(
            id=77,
            first_name='German',
            last_name='Lauren',
            allegation_count=1,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            race='Black',
            rank='Officer',
            last_unit=unit,
            birth_year=1950,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            trr_percentile=None,
            complaint_percentile=None,
            civilian_allegation_percentile=None,
            internal_allegation_percentile=None
        )
        pinned_trr = TRRFactory(officer=temp_officer)
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2])
        pinboard.allegations.set([pinned_allegation_1, pinned_allegation_2, pinned_allegation_3])
        pinboard.trrs.set([pinned_trr])
        not_relevant_allegation = AllegationFactory(crid='999')

        officer_coaccusal_11 = OfficerFactory(
            id=11,
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=1,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            race='Black',
            rank='Police Officer',
            last_unit=unit,
            birth_year=1950,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
        )
        officer_coaccusal_21 = OfficerFactory(
            id=21,
            first_name='Ellis',
            last_name='Skol',
            allegation_count=1,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            race='Black',
            rank='Senior Officer',
            last_unit=unit,
            birth_year=1950,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            trr_percentile='33.33',
            complaint_percentile='44.44',
            civilian_allegation_percentile='55.55',
            internal_allegation_percentile=None,
        )
        OfficerFactory(id=99, first_name='Not Relevant', last_name='Officer')

        allegation_11 = AllegationFactory(crid='11')
        allegation_12 = AllegationFactory(crid='12')
        allegation_13 = AllegationFactory(crid='13')
        allegation_14 = AllegationFactory(crid='14')
        allegation_15 = AllegationFactory(crid='15')
        OfficerAllegationFactory(allegation=allegation_11, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_12, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_13, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_14, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_15, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_11, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=allegation_12, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=allegation_13, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=allegation_14, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=allegation_15, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=officer_coaccusal_11)

        allegation_21 = AllegationFactory(crid='21')
        allegation_22 = AllegationFactory(crid='22')
        allegation_23 = AllegationFactory(crid='23')
        allegation_24 = AllegationFactory(crid='24')
        OfficerAllegationFactory(allegation=allegation_21, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_22, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_23, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_24, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_21, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_22, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_23, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_24, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=officer_coaccusal_21)

        allegation_coaccusal_12 = OfficerFactory(
            id=12,
            first_name='Raymond',
            last_name='Piwinicki',
            allegation_count=1,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            race='Black',
            rank='IPRA investigator',
            last_unit=unit,
            birth_year=1950,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            trr_percentile=None,
            complaint_percentile='99.99',
            civilian_allegation_percentile='77.77',
            internal_allegation_percentile=None,
        )
        allegation_coaccusal_22 = OfficerFactory(
            id=22,
            first_name='Edward',
            last_name='May',
            allegation_count=1,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            race='Black',
            rank='Detective',
            last_unit=unit,
            birth_year=1950,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            trr_percentile=None,
            complaint_percentile=None,
            civilian_allegation_percentile=None,
            internal_allegation_percentile=None,
        )
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_3, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_22)

        OfficerHistoryFactory(officer=officer_coaccusal_11, unit=unit, effective_date=date(2004, 1, 2))
        OfficerHistoryFactory(officer=officer_coaccusal_21, unit=unit, effective_date=date(2004, 1, 2))
        OfficerHistoryFactory(officer=allegation_coaccusal_12, unit=unit, effective_date=date(2004, 1, 2))
        OfficerHistoryFactory(officer=allegation_coaccusal_22, unit=unit, effective_date=date(2004, 1, 2))

        request_url = reverse('api-v2:pinboards-relevant-coaccusals', kwargs={'pk': '66ef1560'})
        response = self.client.get(request_url)
        expect(response.data['count']).to.eq(5)
        expect(response.data['previous']).to.be.none()
        expect(response.data['next']).to.be.none()
        results = [{
            'id': 11,
            'full_name': 'Jerome Finnigan',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/11/jerome-finnigan/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'Police Officer',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004'
            },
            'percentile_trr': '11.1100',
            'percentile_allegation': '22.2200',
            'percentile_allegation_civilian': '33.3300',
            'percentile_allegation_internal': '44.4400',
            'allegation_count': 1,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'coaccusal_count': 5,
        }, {
            'id': 21,
            'full_name': 'Ellis Skol',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/21/ellis-skol/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'Senior Officer',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004'
            },
            'percentile_trr': '33.3300',
            'percentile_allegation': '44.4400',
            'percentile_allegation_civilian': '55.5500',
            'allegation_count': 1,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'coaccusal_count': 4,
        }, {
            'id': 12,
            'full_name': 'Raymond Piwinicki',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/12/raymond-piwinicki/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'IPRA investigator',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004'
            },
            'percentile_allegation': '99.9900',
            'percentile_allegation_civilian': '77.7700',
            'allegation_count': 1,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'coaccusal_count': 3,
        }, {
            'id': 22,
            'full_name': 'Edward May',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/22/edward-may/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'Detective',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004'
            },
            'allegation_count': 1,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'coaccusal_count': 2,
        }, {
            'id': 77,
            'full_name': 'German Lauren',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/77/german-lauren/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'Officer',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004'
            },
            'allegation_count': 1,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'coaccusal_count': 1,
        }]

        expect(response.data['results']).to.eq(results)

    def test_relevant_coaccusals_pagination(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_allegation_1 = AllegationFactory(crid='1')
        pinned_allegation_2 = AllegationFactory(crid='2')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2])
        pinboard.allegations.set([pinned_allegation_1, pinned_allegation_2])
        not_relevant_allegation = AllegationFactory(crid='999')

        unit = PoliceUnitFactory(
            id=4,
            unit_name='004',
            description='District 004',
        )

        officer_coaccusal_11 = OfficerFactory(
            id=11,
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=1,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            race='Black',
            rank='Police Officer',
            last_unit=unit,
            birth_year=1950,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
        )
        officer_coaccusal_21 = OfficerFactory(
            id=21,
            first_name='Ellis',
            last_name='Skol',
            allegation_count=1,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            race='Black',
            rank='Senior Officer',
            last_unit=unit,
            birth_year=1950,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            trr_percentile='33.33',
            complaint_percentile='44.44',
            civilian_allegation_percentile='55.55',
            internal_allegation_percentile=None,
        )
        OfficerFactory(id=99, first_name='Not Relevant', last_name='Officer')

        allegation_11 = AllegationFactory(crid='11')
        allegation_12 = AllegationFactory(crid='12')
        allegation_13 = AllegationFactory(crid='13')
        allegation_14 = AllegationFactory(crid='14')
        OfficerAllegationFactory(allegation=allegation_11, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_12, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_13, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_14, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_11, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=allegation_12, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=allegation_13, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=allegation_14, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=officer_coaccusal_11)

        allegation_21 = AllegationFactory(crid='21')
        allegation_22 = AllegationFactory(crid='22')
        allegation_23 = AllegationFactory(crid='23')
        OfficerAllegationFactory(allegation=allegation_21, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_22, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_23, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_21, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_22, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_23, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=officer_coaccusal_21)

        allegation_coaccusal_12 = OfficerFactory(
            id=12,
            first_name='Raymond',
            last_name='Piwinicki',
            allegation_count=1,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            race='Black',
            rank='IPRA investigator',
            last_unit=unit,
            birth_year=1950,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            trr_percentile=None,
            complaint_percentile='99.99',
            civilian_allegation_percentile='77.77',
            internal_allegation_percentile=None,
        )
        allegation_coaccusal_22 = OfficerFactory(
            id=22,
            first_name='Edward',
            last_name='May',
            allegation_count=1,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            current_badge='456',
            gender='F',
            race='Black',
            rank='Detective',
            last_unit=unit,
            birth_year=1950,
            civilian_compliment_count=2,
            sustained_count=4,
            discipline_count=6,
            trr_count=7,
            major_award_count=8,
            honorable_mention_count=3,
            honorable_mention_percentile='88.8800',
            trr_percentile=None,
            complaint_percentile=None,
            civilian_allegation_percentile=None,
            internal_allegation_percentile=None,
        )
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_22)

        base_url = reverse('api-v2:pinboards-relevant-coaccusals', kwargs={'pk': '66ef1560'})
        first_response = self.client.get(f"{base_url}?{urlencode({'limit': 2})}")
        expect(first_response.status_code).to.eq(status.HTTP_200_OK)
        expect(first_response.data['results']).to.eq([{
            'id': 11,
            'full_name': 'Jerome Finnigan',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/11/jerome-finnigan/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'Police Officer',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004'
            },
            'percentile_trr': '11.1100',
            'percentile_allegation': '22.2200',
            'percentile_allegation_civilian': '33.3300',
            'percentile_allegation_internal': '44.4400',
            'allegation_count': 1,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'coaccusal_count': 4,
        }, {
            'id': 21,
            'full_name': 'Ellis Skol',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/21/ellis-skol/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'Senior Officer',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004'
            },
            'percentile_trr': '33.3300',
            'percentile_allegation': '44.4400',
            'percentile_allegation_civilian': '55.5500',
            'allegation_count': 1,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'coaccusal_count': 3,
        }])
        expect(first_response.data['count']).to.eq(4)
        expect(first_response.data['previous']).to.be.none()
        expect(first_response.data['next']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-coaccusals/?limit=2&offset=2'
        )

        second_response = self.client.get(f"{base_url}?{urlencode({'limit': 2, 'offset': 1})}")
        expect(second_response.status_code).to.eq(status.HTTP_200_OK)
        expect(second_response.data['results']).to.eq([{
            'id': 21,
            'full_name': 'Ellis Skol',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/21/ellis-skol/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'Senior Officer',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004'
            },
            'percentile_trr': '33.3300',
            'percentile_allegation': '44.4400',
            'percentile_allegation_civilian': '55.5500',
            'allegation_count': 1,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'coaccusal_count': 3,
        }, {
            'id': 12,
            'full_name': 'Raymond Piwinicki',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/12/raymond-piwinicki/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'IPRA investigator',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004'
            },
            'percentile_allegation': '99.9900',
            'percentile_allegation_civilian': '77.7700',
            'allegation_count': 1,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'coaccusal_count': 2,
        }])
        expect(second_response.data['count']).to.eq(4)
        expect(second_response.data['previous']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-coaccusals/?limit=2'
        )
        expect(second_response.data['next']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-coaccusals/?limit=2&offset=3'
        )

        last_response = self.client.get(f"{base_url}?{urlencode({'limit': 2, 'offset': 3})}")
        expect(last_response.status_code).to.eq(status.HTTP_200_OK)
        expect(last_response.data['results']).to.eq([{
            'id': 22,
            'full_name': 'Edward May',
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'badge': '456',
            'gender': 'Female',
            'to': '/officer/22/edward-may/',
            'birth_year': 1950,
            'race': 'Black',
            'rank': 'Detective',
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004'
            },
            'allegation_count': 1,
            'civilian_compliment_count': 2,
            'sustained_count': 4,
            'discipline_count': 6,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_count': 3,
            'honorable_mention_percentile': '88.8800',
            'coaccusal_count': 1,
        }])
        expect(last_response.data['count']).to.eq(4)
        expect(last_response.data['previous']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-coaccusals/?limit=2&offset=1'
        )
        expect(last_response.data['next']).to.be.none()

    def test_relevant_complaints_via_accused_officers(self):
        pinned_officer_1 = OfficerFactory(
            id=1,
            rank='Police Officer',
            first_name='Jerome',
            last_name='Finnigan',
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
            allegation_count=2,
        )
        pinned_officer_2 = OfficerFactory(
            id=2,
            rank='Senior Officer',
            first_name='Ellis',
            last_name='Skol',
            trr_percentile='33.33',
            complaint_percentile='44.44',
            civilian_allegation_percentile='55.55',
            internal_allegation_percentile=None,
            allegation_count=1,
        )
        pinned_officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(
            id=99,
            rank='Detective',
            first_name='Edward',
            last_name='May',
            trr_percentile=None,
            complaint_percentile=None,
            civilian_allegation_percentile=None,
            internal_allegation_percentile=None,
            allegation_count=5,
        )

        relevant_allegation_1 = AllegationFactory(
            crid='1',
            incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc),
            most_common_category=AllegationCategoryFactory(
                category='Operation/Personnel Violations',
                allegation_name='Subcategory'
            ),
            point=Point([0.01, 0.02])
        )
        VictimFactory(
            gender='M',
            race='Black',
            age=35,
            allegation=relevant_allegation_1
        )
        relevant_allegation_2 = AllegationFactory(
            crid='2',
            incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc)
        )
        AllegationFactory(crid='not relevant')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2, pinned_officer_3])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=officer_4, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=pinned_officer_2, allegation=relevant_allegation_2)

        request_url = reverse('api-v2:pinboards-relevant-complaints', kwargs={'pk': '66ef1560'})
        response = self.client.get(request_url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq({
            'count': 2,
            'next': None,
            'previous': None,
            'results': [{
                'crid': '2',
                'address': '',
                'category': 'Unknown',
                'incident_date': '2002-02-22',
                'victims': [],
                'to': '/complaint/2/',
                'sub_category': 'Unknown',
                'coaccused': [{
                    'id': 2,
                    'rank': 'Senior Officer',
                    'full_name': 'Ellis Skol',
                    'allegation_count': 1,
                    'percentile_trr': '33.3300',
                    'percentile_allegation': '44.4400',
                    'percentile_allegation_civilian': '55.5500',
                }],
            }, {
                'crid': '1',
                'address': '',
                'category': 'Operation/Personnel Violations',
                'incident_date': '2002-02-21',
                'victims': [{
                    'gender': 'Male',
                    'race': 'Black',
                    'age': 35,
                }],
                'point': {'lon': 0.01, 'lat': 0.02},
                'to': '/complaint/1/',
                'sub_category': 'Subcategory',
                'coaccused': [{
                    'id': 99,
                    'rank': 'Detective',
                    'full_name': 'Edward May',
                    'allegation_count': 5,
                }, {
                    'id': 1,
                    'rank': 'Police Officer',
                    'full_name': 'Jerome Finnigan',
                    'allegation_count': 2,
                    'percentile_trr': '11.1100',
                    'percentile_allegation': '22.2200',
                    'percentile_allegation_civilian': '33.3300',
                    'percentile_allegation_internal': '44.4400',
                }],
            }]
        })

    def test_relevant_complaints_filter_out_pinned_allegations(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_allegation_1 = AllegationFactory(crid='1')
        pinned_allegation_2 = AllegationFactory(crid='2')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2])
        pinboard.allegations.set([pinned_allegation_1, pinned_allegation_2])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=pinned_allegation_1)
        OfficerAllegationFactory(officer=pinned_officer_2, allegation=pinned_allegation_2)
        AllegationFactory(crid='not relevant')

        request_url = reverse('api-v2:pinboards-relevant-complaints', kwargs={'pk': '66ef1560'})
        response = self.client.get(request_url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        })

    def test_relevant_complaints_via_investigator(self):
        pinned_investigator_1 = OfficerFactory(id=1)
        pinned_investigator_2 = OfficerFactory(id=2)
        pinned_investigator_3 = OfficerFactory(id=3)
        not_relevant_officer = OfficerFactory(id=999)
        relevant_allegation_1 = AllegationFactory(crid='1', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        relevant_allegation_2 = AllegationFactory(crid='2', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        relevant_allegation_3 = AllegationFactory(crid='3', incident_date=datetime(2002, 2, 23, tzinfo=pytz.utc))
        not_relevant_allegation = AllegationFactory(crid='999')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_investigator_1, pinned_investigator_2, pinned_investigator_3])
        InvestigatorAllegationFactory(investigator__officer=pinned_investigator_1, allegation=relevant_allegation_1)
        InvestigatorAllegationFactory(investigator__officer=pinned_investigator_2, allegation=relevant_allegation_2)
        InvestigatorAllegationFactory(investigator__officer=pinned_investigator_3, allegation=relevant_allegation_3)
        InvestigatorAllegationFactory(investigator__officer=not_relevant_officer, allegation=not_relevant_allegation)

        request_url = reverse('api-v2:pinboards-relevant-complaints', kwargs={'pk': '66ef1560'})
        response = self.client.get(request_url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        relevant_complaints = response.data['results']
        expect(relevant_complaints).to.have.length(3)
        expect(relevant_complaints[0]['crid']).to.eq('3')
        expect(relevant_complaints[1]['crid']).to.eq('2')
        expect(relevant_complaints[2]['crid']).to.eq('1')

    def test_relevant_complaints_via_police_witnesses(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        not_relevant_officer = OfficerFactory(id=999)
        relevant_allegation_11 = AllegationFactory(crid='11', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        relevant_allegation_12 = AllegationFactory(crid='12', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        relevant_allegation_21 = AllegationFactory(crid='21', incident_date=datetime(2002, 2, 23, tzinfo=pytz.utc))
        not_relevant_allegation = AllegationFactory(crid='999')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2])
        PoliceWitnessFactory(allegation=relevant_allegation_11, officer=pinned_officer_1)
        PoliceWitnessFactory(allegation=relevant_allegation_12, officer=pinned_officer_1)
        PoliceWitnessFactory(allegation=relevant_allegation_21, officer=pinned_officer_2)
        PoliceWitnessFactory(allegation=not_relevant_allegation, officer=not_relevant_officer)

        request_url = reverse('api-v2:pinboards-relevant-complaints', kwargs={'pk': '66ef1560'})
        response = self.client.get(request_url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        relevant_complaints = response.data['results']
        expect(relevant_complaints).to.have.length(3)
        expect(relevant_complaints[0]['crid']).to.eq('21')
        expect(relevant_complaints[1]['crid']).to.eq('12')
        expect(relevant_complaints[2]['crid']).to.eq('11')

    def test_relevant_complaints_pagination(self):
        pinned_investigator_1 = OfficerFactory(id=1)
        pinned_investigator_2 = OfficerFactory(id=2)
        pinned_investigator_3 = OfficerFactory(id=3)
        not_relevant_officer = OfficerFactory(id=999)
        relevant_allegation_1 = AllegationFactory(crid='1', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        relevant_allegation_2 = AllegationFactory(crid='2', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        relevant_allegation_3 = AllegationFactory(crid='3', incident_date=datetime(2002, 2, 23, tzinfo=pytz.utc))
        not_relevant_allegation = AllegationFactory(crid='999')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_investigator_1, pinned_investigator_2, pinned_investigator_3])
        InvestigatorAllegationFactory(investigator__officer=pinned_investigator_1, allegation=relevant_allegation_1)
        InvestigatorAllegationFactory(investigator__officer=pinned_investigator_2, allegation=relevant_allegation_2)
        InvestigatorAllegationFactory(investigator__officer=pinned_investigator_3, allegation=relevant_allegation_3)
        InvestigatorAllegationFactory(investigator__officer=not_relevant_officer, allegation=not_relevant_allegation)

        base_url = reverse('api-v2:pinboards-relevant-complaints', kwargs={'pk': '66ef1560'})
        first_response = self.client.get(f"{base_url}?{urlencode({'limit': 2})}")
        expect(first_response.status_code).to.eq(status.HTTP_200_OK)
        expect(first_response.data['results']).to.eq([{
            'crid': '3',
            'address': '',
            'category': 'Unknown',
            'incident_date': '2002-02-23',
            'victims': [],
            'to': '/complaint/3/',
            'sub_category': 'Unknown',
            'coaccused': [],
        }, {
            'crid': '2',
            'address': '',
            'category': 'Unknown',
            'incident_date': '2002-02-22',
            'victims': [],
            'to': '/complaint/2/',
            'sub_category': 'Unknown',
            'coaccused': [],
        }])
        expect(first_response.data['count']).to.eq(3)
        expect(first_response.data['previous']).to.be.none()
        expect(first_response.data['next']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-complaints/?limit=2&offset=2'
        )

        second_response = self.client.get(f"{base_url}?{urlencode({'limit': 1, 'offset': 1})}")
        expect(second_response.status_code).to.eq(status.HTTP_200_OK)
        expect(second_response.data['results']).to.eq([{
            'crid': '2',
            'address': '',
            'category': 'Unknown',
            'incident_date': '2002-02-22',
            'victims': [],
            'to': '/complaint/2/',
            'sub_category': 'Unknown',
            'coaccused': [],
        }])
        expect(second_response.data['count']).to.eq(3)
        expect(second_response.data['previous']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-complaints/?limit=1'
        )
        expect(second_response.data['next']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-complaints/?limit=1&offset=2'
        )

        last_response = self.client.get(f"{base_url}?{urlencode({'limit': 2, 'offset': 2})}")
        expect(last_response.status_code).to.eq(status.HTTP_200_OK)
        expect(last_response.data['results']).to.eq([{
            'crid': '1',
            'address': '',
            'category': 'Unknown',
            'incident_date': '2002-02-21',
            'victims': [],
            'to': '/complaint/1/',
            'sub_category': 'Unknown',
            'coaccused': [],
        }])
        expect(last_response.data['count']).to.eq(3)
        expect(last_response.data['previous']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-complaints/?limit=2'
        )
        expect(last_response.data['next']).to.be.none()

    def test_latest_retrieved_pinboard_return_null(self):
        # No previous pinboard, data returned should be null
        response = self.client.get(reverse('api-v2:pinboards-latest-retrieved-pinboard'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({})

    def test_latest_retrieved_pinboard_return_null_when_create_is_not_true(self):
        response = self.client.get(reverse('api-v2:pinboards-latest-retrieved-pinboard'), {'create': 'not true'})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({})

    def test_latest_retrieved_pinboard_return_new_empty_pinboard(self):
        example_pinboard_1 = PinboardFactory(
            id='eeee1111',
            title='Example pinboard 1',
            description='Example pinboard 1',
        )
        example_pinboard_2 = PinboardFactory(
            id='eeee2222',
            title='Example pinboard 2',
            description='Example pinboard 2',
        )
        ExamplePinboardFactory(pinboard=example_pinboard_1)
        ExamplePinboardFactory(pinboard=example_pinboard_2)

        response = self.client.get(reverse('api-v2:pinboards-latest-retrieved-pinboard'), {'create': 'true'})
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        response.data['example_pinboards'] = sorted(
            response.data['example_pinboards'],
            key=lambda pinboard: pinboard['id']
        )

        expect(self.client.session.get('owned_pinboards')).to.eq([response.data['id']])
        expect(self.client.session.get('latest_retrieved_pinboard')).to.eq(response.data['id'])

        expect(response.data['id']).to.be.a.string()
        expect(response.data['id']).to.have.length(8)
        expect(response.data).to.eq({
            'id': response.data['id'],
            'title': '',
            'description': '',
            'officer_ids': [],
            'crids': [],
            'trr_ids': [],
            'example_pinboards': [{
                'id': 'eeee1111',
                'title': 'Example pinboard 1',
                'description': 'Example pinboard 1',
            }, {
                'id': 'eeee2222',
                'title': 'Example pinboard 2',
                'description': 'Example pinboard 2',
            }],
        })

    def test_latest_retrieved_pinboard(self):
        # Create a pinboard in current session
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')

        TRRFactory(id=1, officer=OfficerFactory(id=3))

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json'
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

    def test_list(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            PinboardFactory(id='eeee1111', title='Pinboard 1')

        with freeze_time(datetime(2018, 5, 8, 15, 0, 15, tzinfo=pytz.utc)):
            pinboard_2 = PinboardFactory(id='eeee2222', title='Pinboard 2')

        with freeze_time(datetime(2018, 2, 10, 15, 0, 15, tzinfo=pytz.utc)):
            pinboard_3 = PinboardFactory(id='eeee3333', title='Pinboard 3')

        with freeze_time(datetime(2018, 9, 10, 12, 0, 10, tzinfo=pytz.utc)):
            pinboard_2.save()

        with freeze_time(datetime(2018, 8, 20, 12, 0, 10, tzinfo=pytz.utc)):
            pinboard_3.save()

        pinboard_3.last_viewed_at = datetime(2020, 6, 8, 0, 15, 0, tzinfo=pytz.utc)
        pinboard_3.save()

        PinboardFactory()

        session = self.client.session
        session.update({
            'owned_pinboards': ['eeee1111', 'eeee2222', 'eeee3333']
        })
        session.save()

        response = self.client.get(reverse('api-v2:pinboards-list'))
        expect(response.data).to.eq([
            {
                'id': 'eeee3333',
                'title': 'Pinboard 3',
                'created_at': '2018-02-10',
                'last_viewed_at': '2020-06-08T00:15:00Z',
            },
            {
                'id': 'eeee2222',
                'title': 'Pinboard 2',
                'created_at': '2018-05-08',
                'last_viewed_at': '2018-05-08T15:00:15Z',
            },
            {
                'id': 'eeee1111',
                'title': 'Pinboard 1',
                'created_at': '2018-04-03',
                'last_viewed_at': '2018-04-03T12:00:10Z',
            }
        ])

    def test_list_with_detail(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        allegation = AllegationFactory()
        trr = TRRFactory()

        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            pinboard_1 = PinboardFactory(id='eeee1111', title='Pinboard 1')
            pinboard_1.officers.set([officer_1])
            pinboard_1.allegations.set([allegation])

        with freeze_time(datetime(2018, 5, 8, 15, 0, 15, tzinfo=pytz.utc)):
            pinboard_2 = PinboardFactory(id='eeee2222', title='Pinboard 2')
            pinboard_2.officers.set([officer_2])
            pinboard_2.allegations.set([allegation])

        with freeze_time(datetime(2018, 2, 10, 15, 0, 15, tzinfo=pytz.utc)):
            pinboard_3 = PinboardFactory(id='eeee3333', title='Pinboard 3')
            pinboard_3.allegations.set([allegation])
            pinboard_3.trrs.set([trr])

        with freeze_time(datetime(2018, 9, 10, 12, 0, 10, tzinfo=pytz.utc)):
            pinboard_2.save()

        with freeze_time(datetime(2018, 8, 20, 12, 0, 10, tzinfo=pytz.utc)):
            pinboard_3.save()

        PinboardFactory()

        session = self.client.session
        session.update({
            'owned_pinboards': ['eeee1111', 'eeee2222', 'eeee3333']
        })
        session.save()

        response = self.client.get(reverse('api-v2:pinboards-list'), {'detail': True})
        expect(response.data).to.eq([
            {
                'id': 'eeee2222',
                'title': 'Pinboard 2',
                'created_at': '2018-05-08',
                'officer_ids': [officer_2.id],
                'crids': [allegation.crid],
                'trr_ids': [],
                'last_viewed_at': '2018-05-08T15:00:15Z',
            },
            {
                'id': 'eeee1111',
                'title': 'Pinboard 1',
                'created_at': '2018-04-03',
                'officer_ids': [officer_1.id],
                'crids': [allegation.crid],
                'trr_ids': [],
                'last_viewed_at': '2018-04-03T12:00:10Z',
            },
            {
                'id': 'eeee3333',
                'title': 'Pinboard 3',
                'created_at': '2018-02-10',
                'officer_ids': [],
                'crids': [allegation.crid],
                'trr_ids': [trr.id],
                'last_viewed_at': '2018-02-10T15:00:15Z',
            },
        ])

    def test_all_returns_empty_when_not_authenticated(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            pinboard = PinboardFactory(
                id='aaaa1111',
                title='Pinboard 1',
            )
            pinboard.officers.set(OfficerFactory.create_batch(10))
            pinboard.allegations.set(AllegationFactory.create_batch(10))
            pinboard.trrs.set(TRRFactory.create_batch(10))

        base_url = reverse('api-v2:pinboards-all')

        response = self.client.get(f"{base_url}?{urlencode({'limit': 5})}")
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(0)
        expect(response.data['next']).to.eq(None)
        expect(response.data['previous']).to.eq(None)
        expect(response.data['results']).to.eq([])

    def test_all_returns_correct_result_when_authenticated(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            officer_1 = OfficerFactory(
                first_name='Jerome',
                last_name='Finnigan',
                allegation_count=0,
                complaint_percentile='0.0000',
                trr_percentile='0.0000',
                civilian_allegation_percentile='0.0000',
                internal_allegation_percentile='0.0000',
            )
            officer_2 = OfficerFactory(
                first_name='Joe',
                last_name='Parker',
                allegation_count=5,
                complaint_percentile='50.0000',
                trr_percentile='50.0000',
                civilian_allegation_percentile='50.0000',
                internal_allegation_percentile='50.0000',
            )
            officer_3 = OfficerFactory(
                first_name='John',
                last_name='Hurley',
                allegation_count=10,
                complaint_percentile='99.9999',
                trr_percentile='99.9999',
                civilian_allegation_percentile='99.9999',
                internal_allegation_percentile='99.9999',
            )
            allegation_1 = AllegationFactory(
                crid='111111',
                most_common_category=AllegationCategoryFactory(category='Use Of Force'),
                incident_date=datetime(2001, 1, 1, tzinfo=pytz.utc),
            )
            allegation_2 = AllegationFactory(
                crid='222222',
                incident_date=datetime(2002, 2, 2, tzinfo=pytz.utc),
            )
            trr_1 = TRRFactory(
                id='111',
                trr_datetime=datetime(2001, 1, 1, tzinfo=pytz.utc)
            )
            ActionResponseFactory(trr=trr_1, force_type='Use Of Force')
            trr_2 = TRRFactory(
                id='222',
                trr_datetime=datetime(2002, 2, 2, tzinfo=pytz.utc)
            )
            pinboard_1 = PinboardFactory(
                id='aaaa1111',
                title='Pinboard 1',
                description='Pinboard description 1',
                officers=[officer_1, officer_2, officer_3],
                allegations=[allegation_1, allegation_2],
                trrs=[trr_1, trr_2],
            )

        with freeze_time(datetime(2018, 4, 2, 12, 0, 10, tzinfo=pytz.utc)):
            pinboard_2 = PinboardFactory(
                id='bbbb2222',
                title='Pinboard 2',
                description='Pinboard description 2',
            )

        with freeze_time(datetime(2018, 3, 4, 12, 0, 10, tzinfo=pytz.utc)):
            PinboardFactory.create_batch(2, source_pinboard=pinboard_1)
            PinboardFactory.create_batch(3, source_pinboard=pinboard_2)
            PinboardFactory.create_batch(3)

        base_url = reverse('api-v2:pinboards-all')
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(f"{base_url}?{urlencode({'limit': 5})}")
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(10)
        expect(response.data['next']).to.eq(f"http://testserver{base_url}?{urlencode({'limit': 5, 'offset': 5})}")
        expect(response.data['previous']).to.eq(None)
        expect(response.data['results']).to.have.length(5)
        expect(response.data['results']).to.contain({
            'id': 'aaaa1111',
            'title': 'Pinboard 1',
            'description': 'Pinboard description 1',
            'created_at': '2018-04-03T12:00:10Z',
            'officers_count': 3,
            'allegations_count': 2,
            'trrs_count': 2,
            'child_pinboard_count': 2,
            'officers': [
                {
                    'id': officer_3.id,
                    'name': 'John Hurley',
                    'count': 10,
                    'percentile_allegation': '99.9999',
                    'percentile_trr': '99.9999',
                    'percentile_allegation_civilian': '99.9999',
                    'percentile_allegation_internal': '99.9999',
                },
                {
                    'id': officer_2.id,
                    'name': 'Joe Parker',
                    'count': 5,
                    'percentile_allegation': '50.0000',
                    'percentile_trr': '50.0000',
                    'percentile_allegation_civilian': '50.0000',
                    'percentile_allegation_internal': '50.0000',
                },
                {
                    'id': officer_1.id,
                    'name': 'Jerome Finnigan',
                    'count': 0,
                    'percentile_allegation': '0.0000',
                    'percentile_trr': '0.0000',
                    'percentile_allegation_civilian': '0.0000',
                    'percentile_allegation_internal': '0.0000',
                },
            ],
            'allegations': [
                {
                    'crid': '222222',
                    'category': 'Unknown',
                    'incident_date': '2002-02-02',
                },
                {
                    'crid': '111111',
                    'category': 'Use Of Force',
                    'incident_date': '2001-01-01',
                },
            ],
            'trrs': [
                {
                    'id': 222,
                    'trr_datetime': '2002-02-02',
                    'category': 'Unknown',
                },
                {
                    'id': 111,
                    'trr_datetime': '2001-01-01',
                    'category': 'Use Of Force',
                }
            ],
        })
        expect(response.data['results']).to.contain({
            'id': 'bbbb2222',
            'title': 'Pinboard 2',
            'description': 'Pinboard description 2',
            'created_at': '2018-04-02T12:00:10Z',
            'officers_count': 0,
            'allegations_count': 0,
            'trrs_count': 0,
            'child_pinboard_count': 3,
            'officers': [],
            'allegations': [],
            'trrs': [],
        })

    def test_all_return_pinboard_match_title(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            officer_1 = OfficerFactory(
                first_name='Jerome',
                last_name='Finnigan',
                allegation_count=0,
                complaint_percentile='0.0000',
                trr_percentile='0.0000',
                civilian_allegation_percentile='0.0000',
                internal_allegation_percentile='0.0000',
            )
            officer_2 = OfficerFactory(
                first_name='Joe',
                last_name='Parker',
                allegation_count=5,
                complaint_percentile='50.0000',
                trr_percentile='50.0000',
                civilian_allegation_percentile='50.0000',
                internal_allegation_percentile='50.0000',
            )
            officer_3 = OfficerFactory(
                first_name='John',
                last_name='Hurley',
                allegation_count=10,
                complaint_percentile='99.9999',
                trr_percentile='99.9999',
                civilian_allegation_percentile='99.9999',
                internal_allegation_percentile='99.9999',
            )
            allegation_1 = AllegationFactory(
                crid='111111',
                most_common_category=AllegationCategoryFactory(category='Use Of Force'),
                incident_date=datetime(2001, 1, 1, tzinfo=pytz.utc),
            )
            allegation_2 = AllegationFactory(
                crid='222222',
                incident_date=datetime(2002, 2, 2, tzinfo=pytz.utc),
            )
            trr_1 = TRRFactory(
                id='111',
                trr_datetime=datetime(2001, 1, 1, tzinfo=pytz.utc)
            )
            ActionResponseFactory(trr=trr_1, force_type='Use Of Force')
            trr_2 = TRRFactory(
                id='222',
                trr_datetime=datetime(2002, 2, 2, tzinfo=pytz.utc)
            )
            PinboardFactory(
                id='aaaa1111',
                title='Pinboard Title 1',
                description='Pinboard description 1',
                officers=[officer_1, officer_2, officer_3],
                allegations=[allegation_1, allegation_2],
                trrs=[trr_1, trr_2],
            )

        with freeze_time(datetime(2018, 4, 2, 12, 0, 10, tzinfo=pytz.utc)):
            PinboardFactory(
                id='bbbb2222',
                title='Pinboard 2',
                description='Pinboard description 2',
            )

        base_url = reverse('api-v2:pinboards-all')
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(f"{base_url}?match=Title")
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['results']).to.have.length(1)

        expect(response.data['results'][0]).to.eq({
            'id': 'aaaa1111',
            'title': 'Pinboard Title 1',
            'description': 'Pinboard description 1',
            'created_at': '2018-04-03T12:00:10Z',
            'officers_count': 3,
            'allegations_count': 2,
            'trrs_count': 2,
            'child_pinboard_count': 0,
            'officers': [
                {
                    'id': officer_3.id,
                    'name': 'John Hurley',
                    'count': 10,
                    'percentile_allegation': '99.9999',
                    'percentile_trr': '99.9999',
                    'percentile_allegation_civilian': '99.9999',
                    'percentile_allegation_internal': '99.9999',
                },
                {
                    'id': officer_2.id,
                    'name': 'Joe Parker',
                    'count': 5,
                    'percentile_allegation': '50.0000',
                    'percentile_trr': '50.0000',
                    'percentile_allegation_civilian': '50.0000',
                    'percentile_allegation_internal': '50.0000',
                },
                {
                    'id': officer_1.id,
                    'name': 'Jerome Finnigan',
                    'count': 0,
                    'percentile_allegation': '0.0000',
                    'percentile_trr': '0.0000',
                    'percentile_allegation_civilian': '0.0000',
                    'percentile_allegation_internal': '0.0000',
                },
            ],
            'allegations': [
                {
                    'crid': '222222',
                    'category': 'Unknown',
                    'incident_date': '2002-02-02',
                },
                {
                    'crid': '111111',
                    'category': 'Use Of Force',
                    'incident_date': '2001-01-01',
                },
            ],
            'trrs': [
                {
                    'id': 222,
                    'trr_datetime': '2002-02-02',
                    'category': 'Unknown',
                },
                {
                    'id': 111,
                    'trr_datetime': '2001-01-01',
                    'category': 'Use Of Force',
                }
            ],
        })

    def test_all_return_pinboard_match_description(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            officer_1 = OfficerFactory(
                first_name='Jerome',
                last_name='Finnigan',
                allegation_count=0,
                complaint_percentile='0.0000',
                trr_percentile='0.0000',
                civilian_allegation_percentile='0.0000',
                internal_allegation_percentile='0.0000',
            )
            officer_2 = OfficerFactory(
                first_name='Joe',
                last_name='Parker',
                allegation_count=5,
                complaint_percentile='50.0000',
                trr_percentile='50.0000',
                civilian_allegation_percentile='50.0000',
                internal_allegation_percentile='50.0000',
            )
            officer_3 = OfficerFactory(
                first_name='John',
                last_name='Hurley',
                allegation_count=10,
                complaint_percentile='99.9999',
                trr_percentile='99.9999',
                civilian_allegation_percentile='99.9999',
                internal_allegation_percentile='99.9999',
            )
            allegation_1 = AllegationFactory(
                crid='111111',
                most_common_category=AllegationCategoryFactory(category='Use Of Force'),
                incident_date=datetime(2001, 1, 1, tzinfo=pytz.utc),
            )
            allegation_2 = AllegationFactory(
                crid='222222',
                incident_date=datetime(2002, 2, 2, tzinfo=pytz.utc),
            )
            trr_1 = TRRFactory(
                id='111',
                trr_datetime=datetime(2001, 1, 1, tzinfo=pytz.utc)
            )
            ActionResponseFactory(trr=trr_1, force_type='Use Of Force')
            trr_2 = TRRFactory(
                id='222',
                trr_datetime=datetime(2002, 2, 2, tzinfo=pytz.utc)
            )
            PinboardFactory(
                id='aaaa1111',
                title='Pinboard Title 1',
                description='Pinboard description 1',
                officers=[officer_1, officer_2, officer_3],
                allegations=[allegation_1, allegation_2],
                trrs=[trr_1, trr_2],
            )

        with freeze_time(datetime(2018, 4, 2, 12, 0, 10, tzinfo=pytz.utc)):
            PinboardFactory(
                id='bbbb2222',
                title='Pinboard 2',
                description='Pinboard description 2',
            )

        base_url = reverse('api-v2:pinboards-all')
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(f"{base_url}?match=Pinboard description 2")
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['results']).to.have.length(1)

        expect(response.data['results'][0]).to.eq({
            'id': 'bbbb2222',
            'title': 'Pinboard 2',
            'description': 'Pinboard description 2',
            'created_at': '2018-04-02T12:00:10Z',
            'officers_count': 0,
            'allegations_count': 0,
            'trrs_count': 0,
            'child_pinboard_count': 0,
            'officers': [],
            'allegations': [],
            'trrs': [],
        })

    def test_delete_owned_pinboard_success(self):
        session = self.client.session
        session.update({
            'owned_pinboards': ['eeee1111', 'eeee2222', 'eeee3333']
        })
        session.save()
        response = self.client.delete(reverse('api-v2:pinboards-mobile-detail', kwargs={'pk': 'eeee2222'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(self.client.session.get('owned_pinboards')).to.eq(['eeee1111', 'eeee3333'])

    def test_delete_not_owned_pinboard_success(self):
        session = self.client.session
        session.update({
            'owned_pinboards': ['eeee1111', 'eeee2222', 'eeee3333']
        })
        session.save()
        response = self.client.delete(reverse('api-v2:pinboards-mobile-detail', kwargs={'pk': 'eeee4444'}))
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(self.client.session.get('owned_pinboards')).to.eq(['eeee1111', 'eeee2222', 'eeee3333'])

    def test_view_owned_pinboard(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            PinboardFactory(
                id='eeee1111',
                title='Pinboard 1',
            )

        with freeze_time(datetime(2018, 3, 3, 12, 0, 20, tzinfo=pytz.utc)):
            PinboardFactory(
                id='eeee2222',
                title='Pinboard 2',
            )

        with freeze_time(datetime(2018, 2, 3, 12, 0, 10, tzinfo=pytz.utc)):
            PinboardFactory(
                id='eeee3333',
                title='Pinboard 3',
            )

        session = self.client.session
        session.update({
            'owned_pinboards': ['eeee1111', 'eeee2222', 'eeee3333']
        })
        session.save()

        with freeze_time(datetime(2018, 5, 3, 12, 0, 10, tzinfo=pytz.utc)):
            response = self.client.post(reverse('api-v2:pinboards-mobile-view', kwargs={'pk': 'eeee2222'}))
            expect(response.status_code).to.eq(status.HTTP_200_OK)
            viewed_pinboard = Pinboard.objects.filter(id='eeee2222').first()
            expect(viewed_pinboard.last_viewed_at).to.eq(datetime(2018, 5, 3, 12, 0, 10, tzinfo=pytz.utc))

    def test_view_not_owned_pinboard(self):
        session = self.client.session
        session.update({
            'owned_pinboards': ['eeee1111', 'eeee2222', 'eeee3333']
        })
        session.save()

        response = self.client.post(reverse('api-v2:pinboards-mobile-view', kwargs={'pk': 'eeee2222'}))
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

    def test_view_not_existed_pinboard(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            PinboardFactory(
                id='eeee1111',
                title='Pinboard 1',
            )

        with freeze_time(datetime(2018, 2, 3, 12, 0, 10, tzinfo=pytz.utc)):
            PinboardFactory(
                id='eeee3333',
                title='Pinboard 3',
            )

        session = self.client.session
        session.update({
            'owned_pinboards': ['eeee1111', 'eeee2222', 'eeee3333']
        })
        session.save()

        response = self.client.post(reverse('api-v2:pinboards-mobile-view', kwargs={'pk': 'eeee2222'}))
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
