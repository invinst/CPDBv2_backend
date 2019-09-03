from datetime import datetime, date, timedelta

from django.urls import reverse
from django.contrib.gis.geos import Point
from django.utils.timezone import now
from mock import patch

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect
from freezegun import freeze_time
import pytz

from analytics.factories import AttachmentTrackingFactory
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory, AreaFactory,
    PoliceWitnessFactory, InvestigatorFactory, InvestigatorAllegationFactory,
    AllegationCategoryFactory, AttachmentFileFactory, OfficerBadgeNumberFactory, VictimFactory
)
from data.constants import MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_AUDIO, MEDIA_TYPE_VIDEO
from cr.tests.mixins import CRTestCaseMixin
from data.cache_managers import officer_cache_manager, allegation_cache_manager
from email_service.factories import EmailTemplateFactory
from email_service.constants import CR_ATTACHMENT_REQUEST


class CRViewSetTestCase(CRTestCaseMixin, APITestCase):
    @freeze_time('2018-04-04 12:00:01', tz_offset=0)
    def setUp(self):
        super(CRViewSetTestCase, self).setUp()
        self.maxDiff = None

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
            complaint_percentile=0.0,
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
            officer=officer1, allegation=allegation,
            final_finding='SU', disciplined=True,
            final_outcome='Separation', recc_outcome='10 Day Suspension',
            start_date=date(2003, 3, 20), end_date=date(2006, 5, 26),
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
            current_rank='IPRA investigator'
        )

        AttachmentFileFactory(
            tag='TRR',
            allegation=allegation,
            title='CR document',
            id='123456',
            url='http://cr-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            tag='TRR',
            allegation=allegation, title='CR arrest report document',
            url='http://cr-document.com/', file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            tag='AR',
            allegation=allegation,
            title='CR document 2',
            id='654321',
            url='http://AR-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )

        officer_cache_manager.build_cached_columns()
        allegation_cache_manager.cache_data()

        response = self.client.get(reverse('api-v2:cr-detail', kwargs={'pk': '12345'}))
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
                    'gender': 'Male',
                    'race': 'White',
                    'rank': 'Officer',
                    'birth_year': 1993,
                    'recommended_outcome': '10 Day Suspension',
                    'final_outcome': 'Separation',
                    'final_finding': 'Sustained',
                    'category': 'Operation/Personnel Violations',
                    'complaint_count': 1,
                    'sustained_count': 1,
                    'complaint_percentile': 0.0,
                    'percentile': {
                        'percentile_allegation': '0.0000',
                        'percentile_allegation_civilian': '1.1000',
                        'percentile_allegation_internal': '2.2000',
                        'percentile_trr': '3.3000',
                        'year': 2016,
                    },

                    'disciplined': True
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
                    'percentile_allegation_civilian': 7.7,
                    'percentile_allegation_internal': 8.8,
                },
                {
                    'involved_type': 'police_witness',
                    'officer_id': 3,
                    'full_name': 'Raymond Piwinicki',
                    'allegation_count': 1,
                    'sustained_count': 1,
                    'percentile_trr': 5.5,
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
            complaint_percentile=0.0,
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
            final_outcome='Separation', recc_outcome='10 Day Suspension',
            start_date=date(2003, 3, 20), end_date=date(2006, 5, 26),
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
            complaint_percentile=6.6,
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
            allegation=allegation,
            title='CR document',
            id='123456',
            url='http://cr-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            tag='AR',
            allegation=allegation,
            title='CR document 2',
            id='654321',
            url='http://AR-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )

        officer_cache_manager.build_cached_columns()
        allegation_cache_manager.cache_data()

        response = self.client.get(reverse('api-v2:cr-detail', kwargs={'pk': '12345'}))
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
                    'gender': 'Male',
                    'race': 'White',
                    'rank': 'Officer',
                    'birth_year': 1993,
                    'recommended_outcome': '10 Day Suspension',
                    'final_outcome': 'Separation',
                    'final_finding': 'Sustained',
                    'category': 'Operation/Personnel Violations',
                    'complaint_count': 1,
                    'sustained_count': 1,
                    'complaint_percentile': 0.0,
                    'percentile': {
                        'percentile_allegation': '0.0000',
                        'percentile_allegation_civilian': '1.1000',
                        'percentile_allegation_internal': '2.2000',
                        'percentile_trr': '3.3000',
                        'year': 2016,
                    },

                    'disciplined': True
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
                    'percentile_allegation_civilian': 7.7,
                    'percentile_allegation_internal': 8.8,
                },
                {
                    'involved_type': 'investigator',
                    'officer_id': 2,
                    'full_name': 'Jerome Finnigan',
                    'badge': 'CPD',
                    'percentile_allegation_civilian': 7.7,
                    'percentile_allegation_internal': 8.8,
                },
                {
                    'involved_type': 'investigator',
                    'officer_id': 1,
                    'full_name': 'Ellis Skol',
                    'badge': 'CPD',
                    'percentile_allegation_civilian': 7.7,
                    'percentile_allegation_internal': 8.8,
                },
                {
                    'involved_type': 'police_witness',
                    'officer_id': 3,
                    'full_name': 'Raymond Piwinicki',
                    'allegation_count': 1,
                    'sustained_count': 1,
                    'percentile_trr': 5.5,
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

    def test_retrieve_no_match(self):
        response = self.client.get(reverse('api-v2:cr-detail', kwargs={'pk': 321}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    @patch('cr.views.send_attachment_request_email')
    def test_request_document(self, mock_send_attachment_request_email):
        EmailTemplateFactory(type=CR_ATTACHMENT_REQUEST)
        AllegationFactory(crid='112233')
        response = self.client.post(
            reverse('api-v2:cr-request-document', kwargs={'pk': '112233'}),
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
            reverse('api-v2:cr-request-document', kwargs={'pk': allegation.crid}),
            {'email': 'valid_email@example.com'}
        )

        response2 = self.client.post(
            reverse('api-v2:cr-request-document', kwargs={'pk': allegation.crid}),
            {'email': 'valid_email@example.com'}
        )
        expect(response2.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response2.data).to.eq({
            'message': 'Email already added',
            'crid': '112233'
        })

    def test_request_document_without_email(self):
        AllegationFactory(crid='321')
        response = self.client.post(reverse('api-v2:cr-request-document', kwargs={'pk': 321}))
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({
            'message': 'Please enter a valid email'
        })

    def test_request_document_with_invalid_email(self):
        AllegationFactory(crid='321')
        response = self.client.post(reverse('api-v2:cr-request-document', kwargs={'pk': 321}),
                                    {'email': 'invalid@email'})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({
            'message': 'Please enter a valid email'
        })

    def test_request_document_with_invalid_allegation(self):
        response = self.client.post(reverse('api-v2:cr-request-document', kwargs={'pk': 321}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_request_complaint_summary(self):
        allegation = AllegationFactory(crid='11',
                                       incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc),
                                       summary='Summary')
        category = AllegationCategoryFactory(category='Use of Force')
        OfficerAllegationFactory(
            allegation=allegation,
            officer=OfficerFactory(appointed_date=date(2001, 1, 1)),
            start_date=date(2003, 2, 28),
            end_date=date(2004, 4, 28),
            allegation_category=category
        )
        OfficerAllegationFactory(
            allegation=allegation,
            officer=OfficerFactory(appointed_date=date(2001, 1, 1)),
            start_date=date(2003, 2, 28),
            end_date=date(2004, 4, 28),
            allegation_category=None
        )

        officer_cache_manager.build_cached_yearly_percentiles()
        officer_cache_manager.build_cached_columns()
        allegation_cache_manager.cache_data()

        response = self.client.get(reverse('api-v2:cr-complaint-summaries'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([{
            'crid': '11',
            'category_names': ['Unknown', 'Use of Force'],
            'incident_date': '2002-02-28',
            'summary': 'Summary'
        }])

    def test_cr_new_documents(self):
        three_month_ago = now() - timedelta(weeks=12)
        allegation_1 = AllegationFactory(crid='123', incident_date=datetime(2001, 2, 28, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(crid='456', incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc))
        allegation_3 = AllegationFactory(crid='789', incident_date=datetime(2003, 2, 28, tzinfo=pytz.utc))
        allegation_4 = AllegationFactory(crid='321', incident_date=datetime(2004, 2, 28, tzinfo=pytz.utc))
        allegation_5 = AllegationFactory(crid='987', incident_date=datetime(2005, 2, 28, tzinfo=pytz.utc))

        allegation_category_1 = AllegationCategoryFactory(id=1, category='Category 1')
        allegation_category_12 = AllegationCategoryFactory(id=2, category='Category 2')

        OfficerAllegationFactory(allegation=allegation_1, allegation_category=allegation_category_1)
        OfficerAllegationFactory(allegation=allegation_1, allegation_category=allegation_category_1)
        OfficerAllegationFactory(allegation=allegation_1, allegation_category=allegation_category_12)

        AttachmentFileFactory(
            allegation=allegation_1,
            title='CR document 1',
            id='1',
            tag='CR',
            url='http://cr-document.com/1',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url1',
            external_created_at=three_month_ago + timedelta(days=10)
        )
        AttachmentFileFactory(
            allegation=allegation_1,
            title='CR document 1',
            id='111',
            tag='CR',
            url='http://cr-document.com/111',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url111',
            external_created_at=three_month_ago + timedelta(days=9),
            show=False
        )
        AttachmentFileFactory(
            allegation=allegation_1,
            title='CR document 2',
            id='2',
            tag='CR',
            url='http://cr-document.com/2',
            file_type=MEDIA_TYPE_DOCUMENT,
            external_created_at=three_month_ago + timedelta(days=5)
        )

        AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 3',
            id='3',
            tag='CR',
            url='http://cr-document.com/3',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url3',
            external_created_at=three_month_ago + timedelta(days=6)
        )

        AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 4',
            id='4',
            tag='OCIR',
            url='http://cr-document.com/4',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url4',
            external_created_at=three_month_ago + timedelta(days=10)
        )

        AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 5',
            id='5',
            tag='AR',
            url='http://cr-document.com/5',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url5',
            external_created_at=three_month_ago + timedelta(days=11)
        )

        AttachmentFileFactory(
            allegation=allegation_3,
            title='CR document 6',
            id='6',
            tag='CR',
            url='http://cr-document.com/6',
            file_type=MEDIA_TYPE_AUDIO,
            preview_image_url='http://preview.com/url6',
            external_created_at=three_month_ago + timedelta(days=12)
        )

        AttachmentFileFactory(
            allegation=allegation_3,
            title='CR document 7',
            id='7',
            tag='CR',
            url='http://cr-document.com/7',
            file_type=MEDIA_TYPE_VIDEO,
            preview_image_url='http://preview.com/url7',
            external_created_at=three_month_ago + timedelta(days=13)
        )

        attachment_file_1 = AttachmentFileFactory(
            title='Tracking document 1',
            id='8',
            tag='CR',
            url='http://cr-document.com/8',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url8',
            allegation=allegation_4,
            external_created_at=datetime(2014, 9, 14, 12, 0, 1, tzinfo=pytz.utc)
        )

        attachment_file_2 = AttachmentFileFactory(
            title='Tracking document 2',
            id='9',
            tag='CR',
            url='http://cr-document.com/9',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url9',
            allegation=allegation_4,
            external_created_at=datetime(2015, 9, 14, 12, 0, 1, tzinfo=pytz.utc)
        )

        AttachmentFileFactory(
            title='Not appear attachment',
            id=10,
            tag='CR',
            url='http://cr-document.com/10',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url10',
            allegation=allegation_4,
            external_created_at=datetime(2015, 6, 13, 12, 0, 1, tzinfo=pytz.utc)
        )

        attachment_file_3 = AttachmentFileFactory(
            title='Tracking document 3',
            id='11',
            tag='CR',
            url='http://cr-document.com/11',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url11',
            allegation=allegation_5,
            external_created_at=datetime(2015, 9, 14, 12, 0, 1, tzinfo=pytz.utc)
        )

        with freeze_time(datetime(2018, 8, 14, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_1)

        with freeze_time(datetime(2018, 9, 14, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_2)

        with freeze_time(datetime(2018, 7, 14, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_3)

        allegation_cache_manager.cache_data()

        response = self.client.get(reverse('api-v2:cr-list-by-new-document'), {'limit': 5})

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(len(response.data)).to.eq(4)
        expect(response.data).to.eq([
            {
                'crid': '321',
                'latest_document': {
                    'id': '9',
                    'title': 'Tracking document 2',
                    'url': 'http://cr-document.com/9',
                    'preview_image_url': 'http://preview.com/url9',
                    'file_type': 'document'
                },
                'num_recent_documents': 1,
                'incident_date': '2004-02-28',
            },
            {
                'crid': '987',
                'latest_document': {
                    'id': '11',
                    'title': 'Tracking document 3',
                    'url': 'http://cr-document.com/11',
                    'preview_image_url': 'http://preview.com/url11',
                    'file_type': 'document'
                },
                'num_recent_documents': 1,
                'incident_date': '2005-02-28',
            },
            {
                'crid': '123',
                'latest_document': {
                    'id': '1',
                    'title': 'CR document 1',
                    'url': 'http://cr-document.com/1',
                    'preview_image_url': 'http://preview.com/url1',
                    'file_type': 'document'
                },
                'num_recent_documents': 2,
                'incident_date': '2001-02-28',
                'category': 'Category 1'
            },
            {
                'crid': '456',
                'latest_document': {
                    'id': '3',
                    'title': 'CR document 3',
                    'url': 'http://cr-document.com/3',
                    'preview_image_url': 'http://preview.com/url3',
                    'file_type': 'document'
                },
                'num_recent_documents': 1,
                'incident_date': '2002-02-28',
            },
        ])
