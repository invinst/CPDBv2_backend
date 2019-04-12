from datetime import datetime

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect
import pytz

from pinboard.models import Pinboard
from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory
from pinboard.factories import PinboardFactory
from trr.factories import TRRFactory


class PinboardAPITestCase(APITestCase):
    def test_retrieve_pinboard(self):
        PinboardFactory(
            id='f871a13f',
            title='My Pinboard',
            description='abc',
        )

        response = self.client.get(reverse('api-v2:pinboards-detail', kwargs={'pk': 'f871a13f'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 'f871a13f',
            'title': 'My Pinboard',
            'officer_ids': [],
            'crids': [],
            'trr_ids': [],
            'description': 'abc',
        })

        # `id` is case-insensitive
        response = self.client.get(reverse('api-v2:pinboards-detail', kwargs={'pk': 'F871A13F'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 'f871a13f',
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

    def test_social_graph(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')
        officer_4 = OfficerFactory(id=8565, first_name='William', last_name='People')
        officer_5 = OfficerFactory(id=8566, first_name='John', last_name='Sena')
        officer_6 = OfficerFactory(id=8567, first_name='Tom', last_name='Cruise')
        officer_7 = OfficerFactory(id=8568, first_name='Robert', last_name='Long')
        officer_8 = OfficerFactory(id=8569, first_name='Jaeho', last_name='Jung')

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
        allegation_4 = AllegationFactory(
            crid='987',
            is_officer_complaint=False,
            incident_date=datetime(2008, 12, 31, tzinfo=pytz.utc)
        )
        allegation_5 = AllegationFactory(
            crid='555',
            is_officer_complaint=False,
            incident_date=datetime(2009, 12, 31, tzinfo=pytz.utc)
        )
        allegation_6 = AllegationFactory(
            crid='666',
            is_officer_complaint=False,
            incident_date=datetime(2010, 12, 31, tzinfo=pytz.utc)
        )
        allegation_7 = AllegationFactory(
            crid='777',
            is_officer_complaint=False,
            incident_date=datetime(2011, 12, 31, tzinfo=pytz.utc)
        )
        allegation_8 = AllegationFactory(
            crid='888',
            is_officer_complaint=False,
            incident_date=datetime(2012, 12, 31, tzinfo=pytz.utc)
        )
        allegation_9 = AllegationFactory(
            crid='999',
            is_officer_complaint=False,
            incident_date=datetime(2013, 12, 31, tzinfo=pytz.utc)
        )
        allegation_10 = AllegationFactory(
            crid='1000',
            is_officer_complaint=False,
            incident_date=datetime(2014, 12, 31, tzinfo=pytz.utc)
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

        OfficerAllegationFactory(id=8, officer=officer_2, allegation=allegation_4)
        OfficerAllegationFactory(id=9, officer=officer_7, allegation=allegation_4)
        OfficerAllegationFactory(id=10, officer=officer_2, allegation=allegation_5)
        OfficerAllegationFactory(id=11, officer=officer_7, allegation=allegation_5)

        OfficerAllegationFactory(id=12, officer=officer_3, allegation=allegation_6)
        OfficerAllegationFactory(id=13, officer=officer_5, allegation=allegation_6)
        OfficerAllegationFactory(id=14, officer=officer_3, allegation=allegation_7)
        OfficerAllegationFactory(id=15, officer=officer_5, allegation=allegation_7)
        OfficerAllegationFactory(id=16, officer=officer_3, allegation=allegation_8)
        OfficerAllegationFactory(id=17, officer=officer_6, allegation=allegation_8)
        OfficerAllegationFactory(id=18, officer=officer_3, allegation=allegation_9)
        OfficerAllegationFactory(id=19, officer=officer_6, allegation=allegation_9)

        OfficerAllegationFactory(id=20, officer=officer_3, allegation=allegation_10)
        OfficerAllegationFactory(id=21, officer=officer_8, allegation=allegation_10)

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
                {'full_name': 'John Sena', 'id': 8566},
                {'full_name': 'Robert Long', 'id': 8568},
                {'full_name': 'Tom Cruise', 'id': 8567},
                {'full_name': 'William People', 'id': 8565},
            ],
            'coaccused_data': [
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
                    'officer_id_1': 8563,
                    'officer_id_2': 8568,
                    'incident_date': datetime(2009, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8564,
                    'officer_id_2': 8566,
                    'incident_date': datetime(2011, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 2
                },
                {
                    'officer_id_1': 8564,
                    'officer_id_2': 8567,
                    'incident_date': datetime(2013, 12, 31, 0, 0, tzinfo=pytz.utc),
                    'accussed_count': 2
                },
            ],
            'list_event': [
                '2006-12-31 00:00:00+00:00',
                '2007-12-31 00:00:00+00:00',
                '2009-12-31 00:00:00+00:00',
                '2011-12-31 00:00:00+00:00',
                '2013-12-31 00:00:00+00:00',
            ]
        }

        response = self.client.get(reverse('api-v2:pinboards-social-graph', kwargs={'pk': pinboard.id}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)
