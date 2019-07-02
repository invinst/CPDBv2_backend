from datetime import datetime, date
from urllib.parse import urlencode

from django.contrib.gis.geos import Point
from django.conf import settings
from django.urls import reverse

import pytz
from mock import patch, Mock, PropertyMock
from rest_framework import status
from rest_framework.test import APITestCase
from robber import expect

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
    OfficerYearlyPercentileFactory,
    VictimFactory,
)
from pinboard.factories import PinboardFactory
from pinboard.models import Pinboard
from trr.factories import TRRFactory, ActionResponseFactory


@patch('shared.serializer.MAX_VISUAL_TOKEN_YEAR', 2016)
class PinboardViewSetTestCase(APITestCase):
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
            {
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'trr_ids': [1],
                'description': 'abc',
            }
        )

        owned_pinboards.append(response.data['id'])

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

        owned_pinboards.append(response.data['id'])

        # Try updating the old pinboardresponse = self.client.put(
        response = self.client.put(
            reverse('api-v2:pinboards-detail', kwargs={'pk': owned_pinboards[0]}),
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

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'address': '16XX N TALMAN AVE, CHICAGO IL',
                'coaccused': [{
                    'id': 1,
                    'full_name': 'Jesse Pinkman',
                    'complaint_count': 6,
                    'sustained_count': 5,
                    'birth_year': 1940,
                    'complaint_percentile': 0.0,
                    'recommended_outcome': '11 Day Suspension',
                    'final_outcome': 'Separation',
                    'final_finding': 'Sustained',
                    'category': 'Use Of Force',
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
                    },
                }],
                'sub_category': 'Miscellaneous',
                'to': '/complaint/123/',
                'crid': '123',
                'incident_date': '2002-01-01',
                'point': {'lon': -35.5, 'lat': 68.9},
                'most_common_category': 'Use Of Force',
                'victims': [{
                    'gender': 'Female',
                    'race': 'White',
                    'age': 40,
                }]
            },
            {
                'address': '17XX N TALMAN AVE, CHICAGO IL',
                'coaccused': [{
                    'id': 2,
                    'full_name': 'Walter White',
                    'complaint_count': 6,
                    'sustained_count': 5,
                    'birth_year': 1940,
                    'complaint_percentile': 0.0,
                    'recommended_outcome': '10 Day Suspension',
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
                    },
                }],
                'sub_category': 'Miscellaneous',
                'to': '/complaint/124/',
                'crid': '124',
                'incident_date': '2002-01-01',
                'point': {'lon': -35.5, 'lat': 68.9},
                'most_common_category': 'Verbal Abuse',
                'victims': [{
                    'gender': 'Male',
                    'race': 'White',
                    'age': 40,
                }]
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
            has_unique_name=True
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

        OfficerYearlyPercentileFactory(
            officer=officer,
            year=2002,
            percentile_trr='99.88',
            percentile_allegation=None,
            percentile_allegation_civilian='77.66',
            percentile_allegation_internal='66.55'
        )
        OfficerYearlyPercentileFactory(
            officer=officer,
            year=2003,
            percentile_trr='99.99',
            percentile_allegation='88.88',
            percentile_allegation_civilian='77.77',
            percentile_allegation_internal='66.66'
        )

        OfficerFactory(id=2)

        pinboard = PinboardFactory(officers=(officer,))

        response = self.client.get(reverse('api-v2:pinboards-officers', kwargs={'pk': pinboard.id}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([{
            'id': 123,
            'complaint_count': 20,
            'unit': {
                'id': 4,
                'unit_name': '004',
                'description': 'District 004',
                'long_unit_name': 'Unit 004',
            },
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'active': 'Active',
            'rank': 'Sergeant',
            'full_name': 'Michael Flynn',
            'has_unique_name': True,
            'race': 'Black',
            'badge': '456',
            'historic_badges': ['789'],
            'historic_units': [
                {
                    'id': 4,
                    'unit_name': '004',
                    'description': 'District 004',
                    'long_unit_name': 'Unit 004',
                },
                {
                    'id': 5,
                    'unit_name': '005',
                    'description': 'District 005',
                    'long_unit_name': 'Unit 005',
                }
            ],
            'gender': 'Female',
            'birth_year': 1950,
            'current_salary': 10000,
            'allegation_count': 20,
            'complaint_percentile': 99.99,
            'honorable_mention_count': 3,
            'sustained_count': 4,
            'unsustained_count': 5,
            'discipline_count': 6,
            'civilian_compliment_count': 2,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_percentile': 88.88,
            'to': '/officer/123/michael-flynn/',
            'url': f'{settings.V1_URL}/officer/michael-flynn/123',
            'tags': ['tag1', 'tag2'],
            'coaccusals': [{
                'id': 789,
                'coaccusal_count': 10
            }],
            'percentiles': [
                {
                    'id': 123,
                    'year': 2002,
                    'percentile_trr': '99.8800',
                    'percentile_allegation_civilian': '77.6600',
                    'percentile_allegation_internal': '66.5500',
                },
                {
                    'id': 123,
                    'year': 2003,
                    'percentile_trr': '99.9900',
                    'percentile_allegation': '88.8800',
                    'percentile_allegation_civilian': '77.7700',
                    'percentile_allegation_internal': '66.6600',
                },
            ]
        }])

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
            incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc),
            point=None,
        )
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
                'officers': [
                    {
                        'id': 4,
                        'rank': 'Senior Police Officer',
                        'full_name': 'Raymond Piwinicki',
                        'coaccusal_count': None,
                        'allegation_count': 20,
                        'percentile': {
                            'year': 2016,
                        }
                    },
                    {
                        'id': 2,
                        'rank': 'Detective',
                        'full_name': 'Edward May',
                        'coaccusal_count': None,
                        'allegation_count': 3,
                        'percentile': {
                            'year': 2016,
                            'percentile_trr': '11.1100',
                            'percentile_allegation': '22.2200',
                            'percentile_allegation_civilian': '33.3300',
                            'percentile_allegation_internal': '44.4400',

                        }
                    },
                ],
                'point': None,
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
                    'coaccusal_count': None,
                    'allegation_count': 10,
                    'percentile': {
                        'year': 2016,
                        'percentile_trr': '99.9900',
                        'percentile_allegation': '88.8800',
                        'percentile_allegation_civilian': '77.7700',
                        'percentile_allegation_internal': '66.6600',

                    }
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
        pinned_trr = TRRFactory(
            officer=OfficerFactory(
                id=77,
                rank='Officer',
                first_name='German',
                last_name='Lauren',
                trr_percentile=None,
                complaint_percentile=None,
                civilian_allegation_percentile=None,
                internal_allegation_percentile=None,
                allegation_count=77,
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
            allegation_count=21,
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
            allegation_count=12,
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
            allegation_count=22,
        )
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_3, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_22)

        request_url = reverse('api-v2:pinboards-relevant-coaccusals', kwargs={'pk': '66ef1560'})
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
            'percentile': {
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
            'coaccusal_count': 4,
            'allegation_count': 21,
            'percentile': {
                'year': 2016,
                'percentile_trr': '33.3300',
                'percentile_allegation': '44.4400',
                'percentile_allegation_civilian': '55.5500',
            },
        }, {
            'id': 12,
            'rank': 'IPRA investigator',
            'full_name': 'Raymond Piwinicki',
            'coaccusal_count': 3,
            'allegation_count': 12,
            'percentile': {
                'year': 2016,
                'percentile_allegation': '99.9900',
                'percentile_allegation_civilian': '77.7700',
            },
        }, {
            'id': 22,
            'rank': 'Detective',
            'full_name': 'Edward May',
            'coaccusal_count': 2,
            'allegation_count': 22,
            'percentile': {
                'year': 2016,
            },
        }, {
            'id': 77,
            'rank': 'Officer',
            'full_name': 'German Lauren',
            'coaccusal_count': 1,
            'allegation_count': 77,
            'percentile': {
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
            allegation_count=21,
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
            allegation_count=12,
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
            allegation_count=22,
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
            'allegation_count': 11,
            'percentile': {
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
            'allegation_count': 21,
            'percentile': {
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
            'allegation_count': 21,
            'percentile': {
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
            'allegation_count': 12,
            'percentile': {
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
            'allegation_count': 22,
            'percentile': {
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
            internal_allegation_percentile=None,
            allegation_count=3,
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
                'officers': [{
                    'id': 2,
                    'rank': 'Senior Officer',
                    'full_name': 'Ellis Skol',
                    'coaccusal_count': None,
                    'allegation_count': 3,
                    'percentile': {
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
                'officers': [{
                    'id': 99,
                    'rank': 'Detective',
                    'full_name': 'Edward May',
                    'coaccusal_count': None,
                    'allegation_count': 5,
                    'percentile': {
                        'year': 2016,
                    },
                }, {
                    'id': 1,
                    'rank': 'Police Officer',
                    'full_name': 'Jerome Finnigan',
                    'coaccusal_count': None,
                    'allegation_count': 2,
                    'percentile': {
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
            'officers': [],
            'point': None,
        }, {
            'crid': '2',
            'category': 'Unknown',
            'incident_date': '2002-02-22',
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
            'officers': [],
            'point': None,
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
