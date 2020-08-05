from datetime import datetime, date

from django.urls import reverse
from django.contrib.gis.geos import Point
from mock import patch

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
from data.cache_managers import officer_cache_manager, allegation_cache_manager
from email_service.constants import CR_ATTACHMENT_REQUEST
from email_service.factories import EmailTemplateFactory


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
            birth_year=1993,
            complaint_percentile=4.4,
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
            allegation_count=1,
            sustained_count=1,
        )
        OfficerBadgeNumberFactory(officer=officer1, star='12345', current=True)
        allegation = AllegationFactory(
            crid='12345', point=Point(12, 21), incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc), add1=3510,
            add2='Michigan Ave', city='Chicago', location='Police Communications System', beat=area,
            is_officer_complaint=False, summary='Summary',
            first_start_date=date(2003, 3, 20),
            first_end_date=date(2006, 5, 26)
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
        officer = OfficerFactory(
            id=3,
            first_name='Raymond',
            last_name='Piwinicki',
            appointed_date=date(2001, 5, 1),
            complaint_percentile=4.4,
            trr_percentile=5.5,
            allegation_count=1,
            sustained_count=1,
        )
        OfficerAllegationFactory(
            officer=officer,
            final_finding='SU',
            start_date=date(2003, 2, 28),
            allegation__incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        PoliceWitnessFactory(officer=officer, allegation=allegation)
        investigator = OfficerFactory(
            id=1,
            first_name='Ellis',
            last_name='Skol',
            appointed_date=date(2001, 5, 1),
            complaint_percentile=6.6,
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            allegation_count=1,
            sustained_count=0,
        )
        OfficerAllegationFactory(
            officer=investigator,
            final_finding='NS',
            start_date=date(2003, 2, 28),
            allegation__incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        investigator = InvestigatorFactory(officer=investigator)
        InvestigatorAllegationFactory(
            allegation=allegation,
            investigator=investigator,
        )

        AttachmentFileFactory(
            tag='TRR',
            owner=allegation,
            title='CR document',
            id='123456',
            url='http://cr-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            tag='TRR',
            owner=allegation, title='CR arrest report document',
            url='http://cr-document.com/', file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            tag='AR',
            owner=allegation,
            title='CR document 2',
            id='654321',
            url='http://AR-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )

        officer_cache_manager.build_cached_columns()
        allegation_cache_manager.cache_data()

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
                    'allegation_count': 1,
                    'category': 'Operation/Personnel Violations',
                    'percentile_allegation': '4.4000',
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000',
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
                    'badge': 'CPD',
                    'percentile_allegation': '6.6000',
                    'percentile_allegation_civilian': '7.7000',
                    'percentile_allegation_internal': '8.8000',
                },
                {
                    'involved_type': 'police_witness',
                    'officer_id': 3,
                    'full_name': 'Raymond Piwinicki',
                    'allegation_count': 1,
                    'sustained_count': 1,
                    'percentile_trr': '5.5000',
                    'percentile_allegation': '4.4000',
                }
            ],
            'attachments': [
                {
                    'title': 'CR document',
                    'file_type': 'document',
                    'url': 'http://cr-document.com/',
                    'id': '123456',
                }
            ]
        })

    def test_retrieve_badge(self):
        area = AreaFactory(name='Lincoln Square')
        officer1 = OfficerFactory(
            id=123,
            first_name='Mr',
            last_name='Foo',
            gender='M',
            race='White',
            rank='Officer',
            appointed_date=date(2001, 1, 1),
            birth_year=1993,
            complaint_percentile=4.4,
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
            allegation_count=1,
            sustained_count=1,
        )
        OfficerBadgeNumberFactory(officer=officer1, star='12345', current=True)
        allegation = AllegationFactory(
            crid='12345', point=Point(12, 21), incident_date=datetime(2007, 2, 28, tzinfo=pytz.utc), add1=3510,
            add2='Michigan Ave', city='Chicago', location='Police Communications System', beat=area,
            is_officer_complaint=False, summary='Summary',
            first_start_date=date(2003, 3, 20),
            first_end_date=date(2006, 5, 26)
        )
        ComplainantFactory(allegation=allegation, gender='M', race='Black', age='18')
        VictimFactory(allegation=allegation, gender='M', race='Black', age=53)
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation, final_finding='SU', disciplined=True,
            final_outcome='Separation', start_date=date(2003, 3, 20), end_date=date(2006, 5, 26),
            allegation_category=AllegationCategoryFactory(
                category='Operation/Personnel Violations',
                allegation_name='Secondary/Special Employment'
            )
        )
        officer = OfficerFactory(
            id=3,
            first_name='Raymond',
            last_name='Piwinicki',
            appointed_date=date(2001, 5, 1),
            complaint_percentile=9.9,
            trr_percentile=5.5,
            allegation_count=1,
            sustained_count=1,
        )
        OfficerAllegationFactory(
            officer=officer,
            final_finding='SU',
            start_date=date(2003, 2, 28),
            allegation__incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        PoliceWitnessFactory(officer=officer, allegation=allegation)
        investigator = OfficerFactory(
            id=1,
            first_name='Ellis',
            last_name='Skol',
            appointed_date=date(2001, 5, 1),
            complaint_percentile=6.6,
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            allegation_count=1,
            sustained_count=0,
        )
        investigator_2 = OfficerFactory(
            id=2,
            first_name='Jerome',
            last_name='Finnigan',
            appointed_date=date(2001, 5, 1),
            complaint_percentile=6.6,
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            allegation_count=1,
            sustained_count=0,
        )
        investigator_3 = OfficerFactory(
            id=4,
            first_name='Edward',
            last_name='May',
            appointed_date=date(2001, 5, 1),
            complaint_percentile=9.9,
            civilian_allegation_percentile=7.7,
            internal_allegation_percentile=8.8,
            allegation_count=1,
            sustained_count=0,
        )
        OfficerBadgeNumberFactory(officer=investigator_2, star='456789', current=True)
        OfficerAllegationFactory(
            officer=investigator,
            final_finding='NS',
            start_date=date(2003, 2, 28),
            allegation__incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc),
            allegation__is_officer_complaint=False
        )
        investigator = InvestigatorFactory(officer=investigator)
        investigator_2 = InvestigatorFactory(officer=investigator_2)
        investigator_3 = InvestigatorFactory(officer=investigator_3)
        investigator_4 = InvestigatorFactory(first_name='Kevin', last_name='Osborn')
        InvestigatorAllegationFactory(
            allegation=allegation,
            investigator=investigator,
            current_star='123456'
        )
        InvestigatorAllegationFactory(
            allegation=allegation,
            investigator=investigator_2,
            current_star=None
        )
        InvestigatorAllegationFactory(
            allegation=allegation,
            investigator=investigator_3,
            current_star=None
        )
        InvestigatorAllegationFactory(
            allegation=allegation,
            investigator=investigator_4,
            current_star=None
        )

        AttachmentFileFactory(
            tag='TRR',
            owner=allegation,
            title='CR document',
            id='123456',
            url='http://cr-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            tag='AR',
            owner=allegation,
            title='CR document 2',
            id='654321',
            url='http://AR-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )

        officer_cache_manager.build_cached_columns()
        allegation_cache_manager.cache_data()

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
                    'allegation_count': 1,
                    'category': 'Operation/Personnel Violations',
                    'percentile_allegation': '4.4000',
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000',
                    'percentile_trr': '3.3000',
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
            'incident_date': '2007-02-28',
            'start_date': '2003-03-20',
            'end_date': '2006-05-26',
            'address': '3510 Michigan Ave, Chicago',
            'location': 'Police Communications System',
            'beat': 'Lincoln Square',
            'involvements': [
                {
                    'involved_type': 'investigator',
                    'full_name': 'Kevin Osborn',
                    'badge': 'COPA/IPRA',
                },
                {
                    'involved_type': 'investigator',
                    'officer_id': 4,
                    'full_name': 'Edward May',
                    'badge': 'COPA/IPRA',
                    'percentile_allegation': '9.9000',
                    'percentile_allegation_civilian': '7.7000',
                    'percentile_allegation_internal': '8.8000',
                },
                {
                    'involved_type': 'investigator',
                    'officer_id': 2,
                    'full_name': 'Jerome Finnigan',
                    'badge': 'CPD',
                    'percentile_allegation': '6.6000',
                    'percentile_allegation_civilian': '7.7000',
                    'percentile_allegation_internal': '8.8000',
                },
                {
                    'involved_type': 'investigator',
                    'officer_id': 1,
                    'full_name': 'Ellis Skol',
                    'badge': 'CPD',
                    'percentile_allegation': '6.6000',
                    'percentile_allegation_civilian': '7.7000',
                    'percentile_allegation_internal': '8.8000',
                },
                {
                    'involved_type': 'police_witness',
                    'officer_id': 3,
                    'full_name': 'Raymond Piwinicki',
                    'allegation_count': 1,
                    'sustained_count': 1,
                    'percentile_allegation': '9.9000',
                    'percentile_trr': '5.5000',
                }
            ],
            'attachments': [
                {
                    'title': 'CR document',
                    'file_type': 'document',
                    'url': 'http://cr-document.com/',
                    'id': '123456',
                }
            ]
        })

    def test_retrieve_not_found(self):
        response = self.client.get(reverse('api-v2:cr-mobile-detail', kwargs={'pk': '45678'}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    @patch('cr.views.send_attachment_request_email')
    def test_request_document(self, mock_send_attachment_request_email):
        EmailTemplateFactory(type=CR_ATTACHMENT_REQUEST)
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
        expect(mock_send_attachment_request_email).to.be.called_once_with(
            'valid_email@example.com',
            attachment_type='cr_request',
            pk='112233',
        )

    def test_request_same_document_twice(self):
        EmailTemplateFactory(type=CR_ATTACHMENT_REQUEST)
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
