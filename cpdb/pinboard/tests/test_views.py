from datetime import datetime
from urllib.parse import urlencode

from django.urls import reverse
from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect
from mock import patch
import pytz

from pinboard.models import Pinboard
from data.factories import (
    OfficerFactory,
    AllegationFactory,
    OfficerAllegationFactory,
    AttachmentFileFactory,
    AllegationCategoryFactory,
    InvestigatorAllegationFactory,
    PoliceWitnessFactory,
)
from pinboard.factories import PinboardFactory
from trr.factories import TRRFactory


@patch('shared.serializer.MAX_VISUAL_TOKEN_YEAR', 2016)
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
            'description': 'abc',
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
            most_common_category=AllegationCategoryFactory(category='Operation/Personnel Violations')
        )
        relevant_allegation_2 = AllegationFactory(
            crid='2',
            incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc)
        )
        not_relevant_allegation = AllegationFactory(crid='not relevant')
        AttachmentFileFactory(
            id=1,
            title='relevant document 1',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            url='http://cr-1-document.com/',
        )
        AttachmentFileFactory(
            id=2,
            title='relevant document 2',
            allegation=relevant_allegation_2,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-2-CR-p1-normal.gif",
            url='http://cr-2-document.com/',
        )
        AttachmentFileFactory(id=998, title='relevant but not show', allegation=relevant_allegation_1, show=False)
        AttachmentFileFactory(id=999, title='not relevant', allegation=not_relevant_allegation, show=True)

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
                'v2_to': '/complaint/2/',
                'officers': [
                    {
                        'id': 4,
                        'rank': 'Senior Police Officer',
                        'full_name': 'Raymond Piwinicki',
                        'coaccusal_count': None,
                        'percentile': {
                            'id': 4,
                            'year': 2016,
                        }
                    },
                    {
                        'id': 2,
                        'rank': 'Detective',
                        'full_name': 'Edward May',
                        'coaccusal_count': None,
                        'percentile': {
                            'id': 2,
                            'year': 2016,
                            'percentile_trr': '11.1100',
                            'percentile_allegation': '22.2200',
                            'percentile_allegation_civilian': '33.3300',
                            'percentile_allegation_internal': '44.4400',

                        }
                    },
                ]
            }
        }, {
            'id': 1,
            'preview_image_url': "https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            'url': 'http://cr-1-document.com/',
            'allegation': {
                'crid': '1',
                'category': 'Operation/Personnel Violations',
                'incident_date': '2002-02-21',
                'v2_to': '/complaint/1/',
                'officers': [{
                    'id': 1,
                    'rank': 'Police Officer',
                    'full_name': 'Jerome Finnigan',
                    'coaccusal_count': None,
                    'percentile': {
                        'id': 1,
                        'year': 2016,
                        'percentile_trr': '99.9900',
                        'percentile_allegation': '88.8800',
                        'percentile_allegation_civilian': '77.7700',
                        'percentile_allegation_internal': '66.6600',

                    }
                }]
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
            title='relevant document 1',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            url='http://cr-1-document.com/',
        )
        AttachmentFileFactory(
            id=2,
            title='relevant document 2',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-2-CR-p1-normal.gif",
            url='http://cr-2-document.com/',
        )
        AttachmentFileFactory(
            id=3,
            title='relevant document 3',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-3-CR-p1-normal.gif",
            url='http://cr-3-document.com/',
        )
        AttachmentFileFactory(
            id=4,
            title='relevant document 4',
            allegation=relevant_allegation_1,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-4-CR-p1-normal.gif",
            url='http://cr-1-document.com/',
        )
        AttachmentFileFactory(
            id=5,
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
        first_response = self.client.get(f"{base_url}?{urlencode({ 'limit': 2 })}")
        expect(first_response.status_code).to.eq(status.HTTP_200_OK)
        expect(first_response.data['results']).to.have.length(2)
        expect(first_response.data['count']).to.eq(5)
        expect(first_response.data['previous']).to.be.none()
        expect(first_response.data['next']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-documents/?limit=2&offset=2'
        )

        second_response = self.client.get(f"{base_url}?{urlencode({ 'limit': 2, 'offset': 2 })}")
        expect(second_response.status_code).to.eq(status.HTTP_200_OK)
        expect(second_response.data['results']).to.have.length(2)
        expect(second_response.data['count']).to.eq(5)
        expect(second_response.data['previous']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-documents/?limit=2'
        )
        expect(second_response.data['next']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-documents/?limit=2&offset=4'
        )

        last_response = self.client.get(f"{base_url}?{urlencode({ 'limit': 2, 'offset': 4 })}")
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
            internal_allegation_percentile='44.44'
        )
        officer_coaccusal_21 = OfficerFactory(
            id=21,
            rank='Senior Officer',
            first_name='Ellis',
            last_name='Skol',
            trr_percentile='33.33',
            complaint_percentile='44.44',
            civilian_allegation_percentile='55.55',
            internal_allegation_percentile=None
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
        )
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_22)

        request_url = reverse('api-v2:pinboards-relevant-coaccusals', kwargs={'pk': '66ef1560'})
        response = self.client.get(request_url)
        expect(response.data['count']).to.eq(4)
        expect(response.data['previous']).to.be.none()
        expect(response.data['next']).to.be.none()
        expect(response.data['results']).to.eq([{
            'id': 11,
            'rank': 'Police Officer',
            'full_name': 'Jerome Finnigan',
            'coaccusal_count': 4,
            'percentile': {
                'id': 11,
                'year': 2016,
                'percentile_trr': '11.1100',
                'percentile_allegation': '22.2200',
                'percentile_allegation_civilian': '33.3300',
                'percentile_allegation_internal': '44.4400',
            },
        }, {
            'id': 21,
            'rank': 'Senior Officer',
            'full_name': 'Ellis Skol',
            'coaccusal_count': 3,
            'percentile': {
                'id': 21,
                'year': 2016,
                'percentile_trr': '33.3300',
                'percentile_allegation': '44.4400',
                'percentile_allegation_civilian': '55.5500',
            },
        }, {
            'id': 12,
            'rank': 'IPRA investigator',
            'full_name': 'Raymond Piwinicki',
            'coaccusal_count': 2,
            'percentile': {
                'id': 12,
                'year': 2016,
                'percentile_allegation': '99.9900',
                'percentile_allegation_civilian': '77.7700',
            },
        }, {
            'id': 22,
            'rank': 'Detective',
            'full_name': 'Edward May',
            'coaccusal_count': 1,
            'percentile': {
                'id': 22,
                'year': 2016,
            },
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
            internal_allegation_percentile='44.44'
        )
        officer_coaccusal_21 = OfficerFactory(
            id=21,
            rank='Senior Officer',
            first_name='Ellis',
            last_name='Skol',
            trr_percentile='33.33',
            complaint_percentile='44.44',
            civilian_allegation_percentile='55.55',
            internal_allegation_percentile=None
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
            'rank': 'Police Officer',
            'full_name': 'Jerome Finnigan',
            'coaccusal_count': 4,
            'percentile': {
                'id': 11,
                'year': 2016,
                'percentile_trr': '11.1100',
                'percentile_allegation': '22.2200',
                'percentile_allegation_civilian': '33.3300',
                'percentile_allegation_internal': '44.4400',
            },
        }, {
            'id': 21,
            'rank': 'Senior Officer',
            'full_name': 'Ellis Skol',
            'coaccusal_count': 3,
            'percentile': {
                'id': 21,
                'year': 2016,
                'percentile_trr': '33.3300',
                'percentile_allegation': '44.4400',
                'percentile_allegation_civilian': '55.5500',
            },
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
            'rank': 'Senior Officer',
            'full_name': 'Ellis Skol',
            'coaccusal_count': 3,
            'percentile': {
                'id': 21,
                'year': 2016,
                'percentile_trr': '33.3300',
                'percentile_allegation': '44.4400',
                'percentile_allegation_civilian': '55.5500',
            },
        }, {
            'id': 12,
            'rank': 'IPRA investigator',
            'full_name': 'Raymond Piwinicki',
            'coaccusal_count': 2,
            'percentile': {
                'id': 12,
                'year': 2016,
                'percentile_allegation': '99.9900',
                'percentile_allegation_civilian': '77.7700',
            },
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
            'rank': 'Detective',
            'full_name': 'Edward May',
            'coaccusal_count': 1,
            'percentile': {
                'id': 22,
                'year': 2016,
            },
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

        request_url = reverse('api-v2:pinboards-relevant-complaints', kwargs={'pk': '66ef1560'})
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
                'v2_to': '/complaint/2/',
                'officers': [{
                    'id': 2,
                    'rank': 'Senior Officer',
                    'full_name': 'Ellis Skol',
                    'coaccusal_count': None,
                    'percentile': {
                        'id': 2,
                        'year': 2016,
                        'percentile_trr': '33.3300',
                        'percentile_allegation': '44.4400',
                        'percentile_allegation_civilian': '55.5500',
                    },
                }],
                'point': None,
            }, {
                'crid': '1',
                'category': 'Operation/Personnel Violations',
                'incident_date': '2002-02-21',
                'v2_to': '/complaint/1/',
                'officers': [{
                    'id': 99,
                    'rank': 'Detective',
                    'full_name': 'Edward May',
                    'coaccusal_count': None,
                    'percentile': {
                        'id': 99,
                        'year': 2016,
                    },
                }, {
                    'id': 1,
                    'rank': 'Police Officer',
                    'full_name': 'Jerome Finnigan',
                    'coaccusal_count': None,
                    'percentile': {
                        'id': 1,
                        'year': 2016,
                        'percentile_trr': '11.1100',
                        'percentile_allegation': '22.2200',
                        'percentile_allegation_civilian': '33.3300',
                        'percentile_allegation_internal': '44.4400',
                    },
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
            'category': 'Unknown',
            'incident_date': '2002-02-23',
            'v2_to': '/complaint/3/',
            'officers': [],
            'point': None,
        }, {
            'crid': '2',
            'category': 'Unknown',
            'incident_date': '2002-02-22',
            'v2_to': '/complaint/2/',
            'officers': [],
            'point': None,
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
            'category': 'Unknown',
            'incident_date': '2002-02-22',
            'v2_to': '/complaint/2/',
            'officers': [],
            'point': None,
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
            'category': 'Unknown',
            'incident_date': '2002-02-21',
            'v2_to': '/complaint/1/',
            'officers': [],
            'point': None,
        }])
        expect(last_response.data['count']).to.eq(3)
        expect(last_response.data['previous']).to.eq(
            'http://testserver/api/v2/pinboards/66ef1560/relevant-complaints/?limit=2'
        )
        expect(last_response.data['next']).to.be.none()
