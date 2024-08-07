from datetime import datetime
from urllib.parse import urlencode
from operator import itemgetter
import json

import pytz
from django.contrib.gis.geos import Point
from django.urls import reverse
from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from robber import expect
from freezegun import freeze_time

from data.cache_managers import allegation_cache_manager
from data.factories import (
    OfficerFactory,
    AllegationFactory,
    AllegationCategoryFactory,
    OfficerAllegationFactory,
    AttachmentFileFactory,
    InvestigatorAllegationFactory,
    PoliceWitnessFactory,
)
from pinboard.factories import PinboardFactory, ExamplePinboardFactory
from pinboard.models import Pinboard
from trr.factories import TRRFactory, ActionResponseFactory


@patch('data.constants.MAX_VISUAL_TOKEN_YEAR', 2016)
class PinboardMobileViewSetTestCase(APITestCase):
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
        response = self.client.get(reverse('api-v2:pinboards-mobile-detail', kwargs={'pk': 'f871a13f'}))
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
        response = self.client.get(reverse('api-v2:pinboards-mobile-detail', kwargs={'pk': cloned_pinboard_id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data['id']).to.eq(cloned_pinboard_id)
        expect(response.data['title']).to.eq('My Pinboard')
        expect(set(response.data['officer_ids'])).to.eq({11, 22})
        expect(set(response.data['crids'])).to.eq({'abc123', 'abc456'})
        expect(set(response.data['trr_ids'])).to.eq({33, 44})
        expect(response.data['description']).to.eq('abc')
        expect(response.data).not_to.contain('example_pinboards')

    def test_retrieve_pinboard_not_found(self):
        PinboardFactory(
            id='d91ba25d',
            title='My Pinboard',
            description='abc',
        )
        expect(Pinboard.objects.count()).to.eq(1)

        response = self.client.get(reverse('api-v2:pinboards-mobile-detail', kwargs={'pk': 'a4f34019'}))

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
            reverse('api-v2:pinboards-mobile-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json',
        )
        pinboard_id = response.data['id']

        response = self.client.put(
            reverse('api-v2:pinboards-mobile-detail', kwargs={'pk': pinboard_id}),
            json.dumps({
                'title': 'New Pinboard',
                'officer_ids': [1],
                'crids': ['456def'],
                'trr_ids': [1, 2],
                'description': 'def',
            }),
            content_type='application/json',
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
            reverse('api-v2:pinboards-mobile-detail', kwargs={'pk': pinboard_id}),
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
            reverse('api-v2:pinboards-mobile-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json',
        )

        owned_pinboards.append(response.data['id'])

        response = self.client.post(
            reverse('api-v2:pinboards-mobile-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json',
        )

        owned_pinboards.append(response.data['id'])

        # Try updating the old pinboardresponse = self.client.put(
        response = self.client.put(
            reverse('api-v2:pinboards-mobile-detail', kwargs={'pk': owned_pinboards[0]}),
            json.dumps({
                'title': 'New Pinboard',
                'officer_ids': [1],
                'crids': ['456def'],
                'trr_ids': [1, 2],
                'description': 'def',
            }),
            content_type='application/json',
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
            reverse('api-v2:pinboards-mobile-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json',
        )
        self.client.cookies.clear()

        response = self.client.put(
            reverse('api-v2:pinboards-mobile-detail', kwargs={'pk': response.data['id']}),
            json.dumps({
                'title': 'New Pinboard',
                'officer_ids': [1],
                'crids': ['456def'],
                'trr_ids': [1, 2],
                'description': 'def',
            }),
            content_type='application/json',
        )

        expect(response.status_code).to.eq(status.HTTP_403_FORBIDDEN)

    def test_create_pinboard(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')

        TRRFactory(id=1, officer=OfficerFactory(id=3))

        response = self.client.post(
            reverse('api-v2:pinboards-mobile-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json',
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
            reverse('api-v2:pinboards-mobile-list'),
            json.dumps({
                'id': ignored_id,
                'title': 'My Pinboard',
                'officer_ids': [],
                'crids': [],
                'trr_ids': [],
                'description': 'abc',
            }),
            content_type='application/json',
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
            'description': 'abc',
            'example_pinboards': []
        })

        expect(Pinboard.objects.filter(id=response.data['id']).exists()).to.be.true()

    def test_create_pinboard_not_found_pinned_item_ids(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')

        TRRFactory(id=1, officer=OfficerFactory(id=3))

        response = self.client.post(
            reverse('api-v2:pinboards-mobile-list'),
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

    def test_latest_retrieved_pinboard_return_null(self):
        # No previous pinboard, data returned should be null
        response = self.client.get(reverse('api-v2:pinboards-mobile-latest-retrieved-pinboard'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({})

    def test_latest_retrieved_pinboard_return_null_when_create_is_not_true(self):
        response = self.client.get(
            reverse('api-v2:pinboards-mobile-latest-retrieved-pinboard'),
            {'create': 'not true'}
        )
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

        response = self.client.get(
            reverse('api-v2:pinboards-mobile-latest-retrieved-pinboard'),
            {'create': 'true'}
        )
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
            reverse('api-v2:pinboards-mobile-list'),
            json.dumps({
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }),
            content_type='application/json',
        )
        pinboard_id = response.data['id']

        # Latest retrieved pinboard is now the above one
        response = self.client.get(reverse('api-v2:pinboards-mobile-latest-retrieved-pinboard'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': pinboard_id,
            'title': 'My Pinboard',
            'officer_ids': [1, 2],
            'crids': ['123abc'],
            'trr_ids': [1],
            'description': 'abc',
        })

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
            point=None,
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

        response = self.client.get(reverse('api-v2:pinboards-mobile-complaints', kwargs={'pk': pinboard.id}))

        results = sorted(response.data, key=itemgetter('crid'))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(results).to.eq([
            {
                'crid': '1000001',
                'incident_date': '2010-01-01',
                'point': {'lon': 1.0, 'lat': 1.0},
                'category': 'Use Of Force',
            },
            {
                'crid': '1000002',
                'incident_date': '2011-01-01',
                'category': 'Verbal Abuse',
            }
        ])

    def test_selected_officers(self):
        officer1 = OfficerFactory(
            id=1, first_name='Daryl', last_name='Mack',
            trr_percentile=12.0000,
            civilian_allegation_percentile=98.4344,
            internal_allegation_percentile=99.7840,
            complaint_percentile=99.3450,
            rank='Police Officer'
        )
        officer2 = OfficerFactory(
            id=2,
            first_name='Ronald', last_name='Watts',
            trr_percentile=0.0000,
            civilian_allegation_percentile=98.4344,
            internal_allegation_percentile=99.7840,
            complaint_percentile=99.5000,
            rank='Detective'
        )
        OfficerFactory(id=3)

        pinboard = PinboardFactory(officers=(officer1, officer2))

        response = self.client.get(reverse('api-v2:pinboards-mobile-officers', kwargs={'pk': pinboard.id}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'id': 1,
                'full_name': 'Daryl Mack',
                'complaint_count': 0,
                'rank': 'Police Officer',
                'percentile_trr': '12.0000',
                'percentile_allegation': '99.3450',
                'percentile_allegation_civilian': '98.4344',
                'percentile_allegation_internal': '99.7840',
            },
            {
                'id': 2,
                'full_name': 'Ronald Watts',
                'complaint_count': 0,
                'rank': 'Detective',
                'percentile_trr': '0.0000',
                'percentile_allegation': '99.5000',
                'percentile_allegation_civilian': '98.4344',
                'percentile_allegation_internal': '99.7840',
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

        response = self.client.get(reverse('api-v2:pinboards-mobile-trrs', kwargs={'pk': pinboard.id}))

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
            internal_allegation_percentile='66.66'
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
            incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc),
            point=None,
        )
        not_relevant_allegation = AllegationFactory(crid='not relevant')
        AttachmentFileFactory(
            id=1,
            file_type='document',
            title='relevant document 1',
            owner=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            url='http://cr-1-document.com/',
        )
        AttachmentFileFactory(
            id=2,
            file_type='document',
            title='relevant document 2',
            owner=relevant_allegation_2,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-2-CR-p1-normal.gif",
            url='http://cr-2-document.com/',
        )
        AttachmentFileFactory(id=998, title='relevant but not show', owner=relevant_allegation_1, show=False)
        AttachmentFileFactory(id=999, title='not relevant', owner=not_relevant_allegation, show=True)

        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2, pinned_officer_3])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=pinned_officer_2, allegation=relevant_allegation_2)
        OfficerAllegationFactory(officer=officer_4, allegation=relevant_allegation_2)

        response = self.client.get(reverse('api-v2:pinboards-mobile-relevant-documents', kwargs={'pk': '66ef1560'}))

        expected_results = [{
            'id': 2,
            'preview_image_url': "https://assets.documentcloud.org/CRID-2-CR-p1-normal.gif",
            'url': 'http://cr-2-document.com/',
            'allegation': {
                'crid': '2',
                'category': 'Unknown',
                'incident_date': '2002-02-22',
                'officers': [
                    {
                        'id': 4,
                        'rank': 'Senior Police Officer',
                        'full_name': 'Raymond Piwinicki',
                    },
                    {
                        'id': 2,
                        'rank': 'Detective',
                        'full_name': 'Edward May',
                        'percentile_trr': '11.1100',
                        'percentile_allegation': '22.2200',
                        'percentile_allegation_civilian': '33.3300',
                        'percentile_allegation_internal': '44.4400',
                    },
                ],
            }
        }, {
            'id': 1,
            'preview_image_url': "https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            'url': 'http://cr-1-document.com/',
            'allegation': {
                'crid': '1',
                'category': 'Operation/Personnel Violations',
                'incident_date': '2002-02-21',
                'officers': [{
                    'id': 1,
                    'rank': 'Police Officer',
                    'full_name': 'Jerome Finnigan',
                    'percentile_trr': '99.9900',
                    'percentile_allegation': '88.8800',
                    'percentile_allegation_civilian': '77.7700',
                    'percentile_allegation_internal': '66.6600',
                }],
                'point': {'lon': 0.01, 'lat': 0.02},
            }
        }]
        expect(response.status_code).to.eq(status.HTTP_200_OK)
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
            owner=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            url='http://cr-1-document.com/',
        )
        AttachmentFileFactory(
            id=2,
            file_type='document',
            title='relevant document 2',
            owner=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-2-CR-p1-normal.gif",
            url='http://cr-2-document.com/',
        )
        AttachmentFileFactory(
            id=3,
            file_type='document',
            title='relevant document 3',
            owner=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-3-CR-p1-normal.gif",
            url='http://cr-3-document.com/',
        )
        AttachmentFileFactory(
            id=4,
            file_type='document',
            title='relevant document 4',
            owner=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-4-CR-p1-normal.gif",
            url='http://cr-1-document.com/',
        )
        AttachmentFileFactory(
            id=5,
            file_type='document',
            title='relevant document 5',
            owner=relevant_allegation_1,
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

        base_url = reverse('api-v2:pinboards-mobile-relevant-documents', kwargs={'pk': '66ef1560'})
        first_response = self.client.get(f"{base_url}?{urlencode({'limit': 2})}")
        expect(first_response.status_code).to.eq(status.HTTP_200_OK)
        expect(first_response.data['results']).to.have.length(2)
        expect(first_response.data['count']).to.eq(5)
        expect(first_response.data['previous']).to.be.none()
        expect(first_response.data['next']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-documents/?limit=2&offset=2'
        )

        second_response = self.client.get(f"{base_url}?{urlencode({'limit': 2, 'offset': 2})}")
        expect(second_response.status_code).to.eq(status.HTTP_200_OK)
        expect(second_response.data['results']).to.have.length(2)
        expect(second_response.data['count']).to.eq(5)
        expect(second_response.data['previous']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-documents/?limit=2'
        )
        expect(second_response.data['next']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-documents/?limit=2&offset=4'
        )

        last_response = self.client.get(f"{base_url}?{urlencode({'limit': 2, 'offset': 4})}")
        expect(last_response.status_code).to.eq(status.HTTP_200_OK)
        expect(last_response.data['results']).to.have.length(1)
        expect(last_response.data['count']).to.eq(5)
        expect(last_response.data['previous']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-documents/?limit=2&offset=2'
        )
        expect(last_response.data['next']).to.be.none()

    def test_relevant_coaccusals(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_allegation_1 = AllegationFactory(crid='1')
        pinned_allegation_2 = AllegationFactory(crid='2')
        pinned_allegation_3 = AllegationFactory(crid='3')
        pinned_trr = TRRFactory(
            officer=OfficerFactory(
                id=77,
                rank='Officer',
                first_name='German',
                last_name='Lauren',
                allegation_count=27,
                trr_percentile=None,
                complaint_percentile=None,
                civilian_allegation_percentile=None,
                internal_allegation_percentile=None,
            )
        )
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
            rank='Police Officer',
            first_name='Jerome',
            last_name='Finnigan',
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
            allegation_count=11,
        )
        officer_coaccusal_21 = OfficerFactory(
            id=21,
            rank='Senior Officer',
            first_name='Ellis',
            last_name='Skol',
            trr_percentile='33.33',
            complaint_percentile='44.44',
            civilian_allegation_percentile='55.55',
            internal_allegation_percentile=None,
            allegation_count=12,
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
            rank='IPRA investigator',
            first_name='Raymond',
            last_name='Piwinicki',
            trr_percentile=None,
            complaint_percentile='99.99',
            civilian_allegation_percentile='77.77',
            internal_allegation_percentile=None,
            allegation_count=13,
        )
        allegation_coaccusal_22 = OfficerFactory(
            id=22,
            rank='Detective',
            first_name='Edward',
            last_name='May',
            trr_percentile=None,
            complaint_percentile=None,
            civilian_allegation_percentile=None,
            internal_allegation_percentile=None,
            allegation_count=14,
        )
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_3, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_22)

        request_url = reverse('api-v2:pinboards-mobile-relevant-coaccusals', kwargs={'pk': '66ef1560'})
        response = self.client.get(request_url)
        expect(response.data['count']).to.eq(5)
        expect(response.data['previous']).to.be.none()
        expect(response.data['next']).to.be.none()
        expect(response.data['results']).to.eq([{
            'id': 11,
            'rank': 'Police Officer',
            'full_name': 'Jerome Finnigan',
            'coaccusal_count': 5,
            'allegation_count': 11,
            'percentile_trr': '11.1100',
            'percentile_allegation': '22.2200',
            'percentile_allegation_civilian': '33.3300',
            'percentile_allegation_internal': '44.4400',
        }, {
            'id': 21,
            'rank': 'Senior Officer',
            'full_name': 'Ellis Skol',
            'coaccusal_count': 4,
            'allegation_count': 12,
            'percentile_trr': '33.3300',
            'percentile_allegation': '44.4400',
            'percentile_allegation_civilian': '55.5500',
        }, {
            'id': 12,
            'rank': 'IPRA investigator',
            'full_name': 'Raymond Piwinicki',
            'coaccusal_count': 3,
            'allegation_count': 13,
            'percentile_allegation': '99.9900',
            'percentile_allegation_civilian': '77.7700',
        }, {
            'id': 22,
            'rank': 'Detective',
            'full_name': 'Edward May',
            'coaccusal_count': 2,
            'allegation_count': 14,
        }, {
            'id': 77,
            'rank': 'Officer',
            'full_name': 'German Lauren',
            'coaccusal_count': 1,
            'allegation_count': 27,
        }])

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

        officer_coaccusal_11 = OfficerFactory(
            id=11,
            rank='Police Officer',
            first_name='Jerome',
            last_name='Finnigan',
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
            allegation_count=11,
        )
        officer_coaccusal_21 = OfficerFactory(
            id=21,
            rank='Senior Officer',
            first_name='Ellis',
            last_name='Skol',
            trr_percentile='33.33',
            complaint_percentile='44.44',
            civilian_allegation_percentile='55.55',
            internal_allegation_percentile=None,
            allegation_count=12,
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
            rank='IPRA investigator',
            first_name='Raymond',
            last_name='Piwinicki',
            trr_percentile=None,
            complaint_percentile='99.99',
            civilian_allegation_percentile='77.77',
            internal_allegation_percentile=None,
            allegation_count=13,
        )
        allegation_coaccusal_22 = OfficerFactory(
            id=22,
            rank='Detective',
            first_name='Edward',
            last_name='May',
            trr_percentile=None,
            complaint_percentile=None,
            civilian_allegation_percentile=None,
            internal_allegation_percentile=None,
            allegation_count=14,
        )
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_22)

        base_url = reverse('api-v2:pinboards-mobile-relevant-coaccusals', kwargs={'pk': '66ef1560'})
        first_response = self.client.get(f"{base_url}?{urlencode({'limit': 2})}")
        expect(first_response.status_code).to.eq(status.HTTP_200_OK)
        expect(first_response.data['results']).to.eq([{
            'id': 11,
            'rank': 'Police Officer',
            'full_name': 'Jerome Finnigan',
            'coaccusal_count': 4,
            'allegation_count': 11,
            'percentile_trr': '11.1100',
            'percentile_allegation': '22.2200',
            'percentile_allegation_civilian': '33.3300',
            'percentile_allegation_internal': '44.4400',
        }, {
            'id': 21,
            'rank': 'Senior Officer',
            'full_name': 'Ellis Skol',
            'coaccusal_count': 3,
            'allegation_count': 12,
            'percentile_trr': '33.3300',
            'percentile_allegation': '44.4400',
            'percentile_allegation_civilian': '55.5500',
        }])
        expect(first_response.data['count']).to.eq(4)
        expect(first_response.data['previous']).to.be.none()
        expect(first_response.data['next']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-coaccusals/?limit=2&offset=2'
        )

        second_response = self.client.get(f"{base_url}?{urlencode({'limit': 2, 'offset': 1})}")
        expect(second_response.status_code).to.eq(status.HTTP_200_OK)
        expect(second_response.data['results']).to.eq([{
            'id': 21,
            'rank': 'Senior Officer',
            'full_name': 'Ellis Skol',
            'coaccusal_count': 3,
            'allegation_count': 12,
            'percentile_trr': '33.3300',
            'percentile_allegation': '44.4400',
            'percentile_allegation_civilian': '55.5500',
        }, {
            'id': 12,
            'rank': 'IPRA investigator',
            'full_name': 'Raymond Piwinicki',
            'coaccusal_count': 2,
            'allegation_count': 13,
            'percentile_allegation': '99.9900',
            'percentile_allegation_civilian': '77.7700',
        }])
        expect(second_response.data['count']).to.eq(4)
        expect(second_response.data['previous']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-coaccusals/?limit=2'
        )
        expect(second_response.data['next']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-coaccusals/?limit=2&offset=3'
        )

        last_response = self.client.get(f"{base_url}?{urlencode({'limit': 2, 'offset': 3})}")
        expect(last_response.status_code).to.eq(status.HTTP_200_OK)
        expect(last_response.data['results']).to.eq([{
            'id': 22,
            'rank': 'Detective',
            'full_name': 'Edward May',
            'coaccusal_count': 1,
            'allegation_count': 14,
        }])
        expect(last_response.data['count']).to.eq(4)
        expect(last_response.data['previous']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-coaccusals/?limit=2&offset=1'
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
            internal_allegation_percentile=None

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
            most_common_category=AllegationCategoryFactory(category='Operation/Personnel Violations'),
            point=Point([0.01, 0.02])
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

        request_url = reverse('api-v2:pinboards-mobile-relevant-complaints', kwargs={'pk': '66ef1560'})
        response = self.client.get(request_url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 2,
            'next': None,
            'previous': None,
            'results': [{
                'crid': '2',
                'category': 'Unknown',
                'incident_date': '2002-02-22',
                'officers': [{
                    'id': 2,
                    'rank': 'Senior Officer',
                    'full_name': 'Ellis Skol',
                    'percentile_trr': '33.3300',
                    'percentile_allegation': '44.4400',
                    'percentile_allegation_civilian': '55.5500',
                }],
            }, {
                'crid': '1',
                'category': 'Operation/Personnel Violations',
                'incident_date': '2002-02-21',
                'officers': [{
                    'id': 99,
                    'rank': 'Detective',
                    'full_name': 'Edward May',
                }, {
                    'id': 1,
                    'rank': 'Police Officer',
                    'full_name': 'Jerome Finnigan',
                    'percentile_trr': '11.1100',
                    'percentile_allegation': '22.2200',
                    'percentile_allegation_civilian': '33.3300',
                    'percentile_allegation_internal': '44.4400',
                }],
                'point': {'lon': 0.01, 'lat': 0.02},
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

        request_url = reverse('api-v2:pinboards-mobile-relevant-complaints', kwargs={'pk': '66ef1560'})
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

        request_url = reverse('api-v2:pinboards-mobile-relevant-complaints', kwargs={'pk': '66ef1560'})
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

        request_url = reverse('api-v2:pinboards-mobile-relevant-complaints', kwargs={'pk': '66ef1560'})
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

        base_url = reverse('api-v2:pinboards-mobile-relevant-complaints', kwargs={'pk': '66ef1560'})
        first_response = self.client.get(f"{base_url}?{urlencode({'limit': 2})}")
        expect(first_response.status_code).to.eq(status.HTTP_200_OK)
        expect(first_response.data['results']).to.eq([{
            'crid': '3',
            'category': 'Unknown',
            'incident_date': '2002-02-23',
            'officers': [],
        }, {
            'crid': '2',
            'category': 'Unknown',
            'incident_date': '2002-02-22',
            'officers': [],
        }])
        expect(first_response.data['count']).to.eq(3)
        expect(first_response.data['previous']).to.be.none()
        expect(first_response.data['next']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-complaints/?limit=2&offset=2'
        )

        second_response = self.client.get(f"{base_url}?{urlencode({'limit': 1, 'offset': 1})}")
        expect(second_response.status_code).to.eq(status.HTTP_200_OK)
        expect(second_response.data['results']).to.eq([{
            'crid': '2',
            'category': 'Unknown',
            'incident_date': '2002-02-22',
            'officers': [],
        }])
        expect(second_response.data['count']).to.eq(3)
        expect(second_response.data['previous']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-complaints/?limit=1'
        )
        expect(second_response.data['next']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-complaints/?limit=1&offset=2'
        )

        last_response = self.client.get(f"{base_url}?{urlencode({'limit': 2, 'offset': 2})}")
        expect(last_response.status_code).to.eq(status.HTTP_200_OK)
        expect(last_response.data['results']).to.eq([{
            'crid': '1',
            'category': 'Unknown',
            'incident_date': '2002-02-21',
            'officers': [],
        }])
        expect(last_response.data['count']).to.eq(3)
        expect(last_response.data['previous']).to.eq(
            'http://testserver/api/v2/mobile/pinboards/66ef1560/relevant-complaints/?limit=2'
        )
        expect(last_response.data['next']).to.be.none()

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
