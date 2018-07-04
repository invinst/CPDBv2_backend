from datetime import datetime, date

from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect
import pytz

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory, AreaFactory,
    PoliceWitnessFactory, InvestigatorFactory, InvestigatorAllegationFactory,
    AllegationCategoryFactory, AttachmentFileFactory, OfficerBadgeNumberFactory, VictimFactory
)
from data.constants import MEDIA_TYPE_DOCUMENT
from cr.tests.mixins import CRTestCaseMixin


class CRMobileViewSetTestCase(CRTestCaseMixin, APITestCase):
    def test_retrieve(self):
        area = AreaFactory(name='Lincoln Square')
        officer1 = OfficerFactory(
            id=123,
            first_name='Mr',
            last_name='Foo',
            gender='M',
            race='White',
            rank='Officer',
            appointed_date=date(2001, 1, 1),
            birth_year=1993
        )
        OfficerBadgeNumberFactory(officer=officer1, star='12345', current=True)
        allegation = AllegationFactory(
            crid='12345', point=Point(12, 21), incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc), add1=3510,
            add2='Michigan Ave', city='Chicago', location='Police Communications System', beat=area,
            is_officer_complaint=False, summary='Summary'
        )
        ComplainantFactory(allegation=allegation, gender='M', race='Black', age='18')
        VictimFactory(allegation=allegation, gender='M', race='Black', age=53)
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation, final_finding='SU',
            final_outcome='Separation', start_date=date(2003, 3, 20), end_date=date(2006, 5, 26),
            allegation_category=AllegationCategoryFactory(
                category='Operation/Personnel Violations',
                allegation_name='Secondary/Special Employment'
            )
        )
        officer = OfficerFactory(id=3, first_name='Raymond', last_name='Piwinicki', appointed_date=date(2001, 5, 1))
        OfficerAllegationFactory(
            officer=officer,
            final_finding='SU',
            start_date=date(2003, 2, 28),
            allegation__incident_date=date(2002, 2, 28),
            allegation__is_officer_complaint=False
        )
        PoliceWitnessFactory(officer=officer, allegation=allegation)
        investigator = OfficerFactory(
            id=1,
            first_name='Ellis',
            last_name='Skol',
            appointed_date=date(2001, 5, 1)
        )
        OfficerAllegationFactory(
            officer=investigator,
            final_finding='NS',
            start_date=date(2003, 2, 28),
            allegation__incident_date=date(2002, 2, 28),
            allegation__is_officer_complaint=False
        )
        investigator = InvestigatorFactory(officer=investigator)
        InvestigatorAllegationFactory(
            allegation=allegation,
            investigator=investigator,
            current_rank='IPRA investigator'
        )

        AttachmentFileFactory(
            allegation=allegation, title='CR document', url='http://cr-document.com/', file_type=MEDIA_TYPE_DOCUMENT
        )

        self.refresh_index()

        response = self.client.get(reverse('api-v2:cr-mobile-detail', kwargs={'pk': '12345'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(dict(response.data)).to.eq({
            'crid': '12345',
            'most_common_category': {
                'category': 'Operation/Personnel Violations',
                'allegation_name': 'Secondary/Special Employment'
            },
            'coaccused': [
                {
                    'id': 123,
                    'full_name': 'Mr Foo',
                    'rank': 'Officer',
                    'final_outcome': 'Separation',
                    'final_finding': 'Sustained',
                    'category': 'Operation/Personnel Violations',
                    'percentile_allegation': 0,
                    'percentile_allegation_civilian': 0,
                    'percentile_allegation_internal': 0,
                    'percentile_trr': 0
                }
            ],
            'complainants': [
                {
                    'race': 'Black',
                    'gender': 'Male',
                    'age': 18
                }
            ],
            'victims': [
                {
                    'race': 'Black',
                    'gender': 'Male',
                    'age': 53
                }
            ],
            'point': {
                'lon': 12.0,
                'lat': 21.0
            },
            'summary': 'Summary',
            'incident_date': '2002-02-28',
            'start_date': '2003-03-20',
            'end_date': '2006-05-26',
            'address': '3510 Michigan Ave, Chicago',
            'location': 'Police Communications System',
            'beat': 'Lincoln Square',
            'involvements': [
                {
                    'involved_type': 'investigator',
                    'officer_id': 1,
                    'full_name': 'Ellis Skol',
                    'current_rank': 'IPRA investigator',
                    'percentile_allegation_civilian': 0,
                    'percentile_allegation_internal': 0,
                    'percentile_trr': 0,
                },
                {
                    'involved_type': 'police_witness',
                    'officer_id': 3,
                    'full_name': 'Raymond Piwinicki',
                    'allegation_count': 1,
                    'sustained_count': 1,
                    'percentile_allegation_civilian': 0,
                    'percentile_allegation_internal': 0,
                    'percentile_trr': 0,
                }
            ],
            'attachments': [
                {
                    'title': 'CR document',
                    'file_type': 'document',
                    'url': 'http://cr-document.com/',
                    'preview_image_url': None
                }
            ]
        })

    def test_retrieve_not_found(self):
        response = self.client.get(reverse('api-v2:cr-mobile-detail', kwargs={'pk': '45678'}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_request_document(self):
        AllegationFactory(crid='112233')
        response = self.client.post(
            reverse('api-v2:cr-mobile-request-document', kwargs={'pk': '112233'}),
            {'email': 'valid_email@example.com'}
        )
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'message': 'Thanks for subscribing',
            'crid': '112233'
        })

    def test_request_same_document_twice(self):
        allegation = AllegationFactory(crid='112233')
        self.client.post(
            reverse('api-v2:cr-mobile-request-document', kwargs={'pk': allegation.crid}),
            {'email': 'valid_email@example.com'}
        )

        response2 = self.client.post(
            reverse('api-v2:cr-mobile-request-document', kwargs={'pk': allegation.crid}),
            {'email': 'valid_email@example.com'}
        )
        expect(response2.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response2.data).to.eq({
            'message': 'Email already added',
            'crid': '112233'
        })

    def test_request_document_without_email(self):
        AllegationFactory(crid='321')
        response = self.client.post(reverse('api-v2:cr-mobile-request-document', kwargs={'pk': 321}))
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({
            'message': 'Please enter a valid email'
        })

    def test_request_document_with_invalid_email(self):
        AllegationFactory(crid='321')
        response = self.client.post(reverse('api-v2:cr-mobile-request-document', kwargs={'pk': 321}),
                                    {'email': 'invalid@email'})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({
            'message': 'Please enter a valid email'
        })

    def test_request_document_with_invalid_allegation(self):
        response = self.client.post(reverse('api-v2:cr-mobile-request-document', kwargs={'pk': 321}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)
