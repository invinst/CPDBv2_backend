from datetime import datetime, date

from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point

from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect
import pytz

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory, AreaFactory, InvolvementFactory,
    AllegationCategoryFactory, AttachmentFileFactory, OfficerBadgeNumberFactory
)
from data.constants import (MEDIA_TYPE_VIDEO, MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_AUDIO)
from .mixins import CRTestCaseMixin


class OfficersViewSetTestCase(CRTestCaseMixin, APITestCase):
    def setUp(self):
        super(OfficersViewSetTestCase, self).setUp()
        self.maxDiff = None

    def test_retrieve(self):
        area = AreaFactory(name='Lincoln Square')
        officer1 = OfficerFactory(id=123, first_name='Mr', last_name='Foo', gender='M', race='White')
        OfficerBadgeNumberFactory(officer=officer1, star='12345', current=True)
        officer2 = OfficerFactory(id=456, first_name='Mrs', last_name='Bar', gender='F', race='Black')
        OfficerBadgeNumberFactory(officer=officer2, star='45678', current=True)
        allegation = AllegationFactory(
            crid='12345', point=Point(12, 21), incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc), add1=3510,
            add2='Michigan Ave', city='Chicago', location='09', beat=area
        )
        ComplainantFactory(allegation=allegation, gender='M', race='Black', age='18')
        ComplainantFactory(allegation=allegation, gender='F', race='White', age='20')
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation, final_finding='SU', recc_outcome='100',
            final_outcome='400', start_date=date(2003, 2, 28), end_date=date(2004, 2, 28),
            allegation_category=AllegationCategoryFactory(
                category='Operation/Personnel Violations',
                allegation_name='NEGLECT OF DUTY/CONDUCT UNBECOMING - ON DUTY')
        )
        OfficerAllegationFactory(
            officer=officer2, allegation=allegation, final_finding='UN', recc_outcome='400',
            final_outcome='800', start_date=date(2005, 2, 28), end_date=date(2006, 2, 28),
            allegation_category=AllegationCategoryFactory(
                category='Use of Force',
                allegation_name='UNNECESSARY PHYSICAL CONTACT - ON DUTY')
        )
        involvedOfficer1 = OfficerFactory(id=1, first_name='Lee', last_name='Skol', gender='F', race='White')
        involvedOfficer2 = OfficerFactory(id=2, first_name='Richard', last_name='Piwinicki', gender='M', race='White')
        involvedOfficer3 = OfficerFactory(id=3, first_name='Jack', last_name='Ipsum', gender='M', race='Black')
        OfficerBadgeNumberFactory(officer=involvedOfficer1, star='11111', current=True)
        OfficerBadgeNumberFactory(officer=involvedOfficer2, star='22222', current=True)
        OfficerBadgeNumberFactory(officer=involvedOfficer3, star='33333', current=True)

        InvolvementFactory(
            allegation=allegation, involved_type='investigator', officer=involvedOfficer1)
        InvolvementFactory(
            allegation=allegation, involved_type='police witnesses', officer=involvedOfficer2)
        InvolvementFactory(
            allegation=allegation, involved_type='police witnesses', officer=involvedOfficer3)

        AttachmentFileFactory(
            allegation=allegation, title='CR audio', url='http://cr-audio.com/', file_type=MEDIA_TYPE_AUDIO
        )

        AttachmentFileFactory(
            allegation=allegation, title='CR video', url='http://cr-video.com/', file_type=MEDIA_TYPE_VIDEO
        )

        AttachmentFileFactory(
            allegation=allegation, title='CR document', url='http://cr-document.com/', file_type=MEDIA_TYPE_DOCUMENT
        )

        self.refresh_index()

        response = self.client.get(reverse('api-v2:cr-detail', kwargs={'pk': '12345'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'crid': '12345',
            'category_names': ['Operation/Personnel Violations', 'Use of Force'],
            'summary': '',
            'coaccused': [
                {
                    'id': 123,
                    'full_name': 'Mr Foo',
                    'gender': 'Male',
                    'race': 'White',
                    'final_finding': 'Sustained',
                    'recc_outcome': 'Reprimand',
                    'final_outcome': 'Separation',
                    'category': 'Operation/Personnel Violations',
                    'subcategory': 'NEGLECT OF DUTY/CONDUCT UNBECOMING - ON DUTY',
                    'start_date': '2003-02-28',
                    'end_date': '2004-02-28',
                    'badge': '12345',
                },
                {
                    'id': 456,
                    'full_name': 'Mrs Bar',
                    'gender': 'Female',
                    'race': 'Black',
                    'final_finding': 'Unfounded',
                    'recc_outcome': 'Separation',
                    'final_outcome': 'Resigned',
                    'category': 'Use of Force',
                    'subcategory': 'UNNECESSARY PHYSICAL CONTACT - ON DUTY',
                    'start_date': '2005-02-28',
                    'end_date': '2006-02-28',
                    'badge': '45678',
                }
            ],
            'complainants': [
                {
                    'race': 'Black',
                    'gender': 'Male',
                    'age': 18
                },
                {
                    'race': 'White',
                    'gender': 'Female',
                    'age': 20
                }
            ],
            'point': {
                'long': 12.0,
                'lat': 21.0
            },
            'incident_date': '2002-02-28',
            'address': '3510 Michigan Ave, Chicago',
            'location': 'Police Communications System',
            'beat': {'name': 'Lincoln Square'},
            'involvements': [
                {
                    'involved_type': 'investigator',
                    'officers': [
                        {
                            'id': 1,
                            'abbr_name': 'L. Skol',
                            'extra_info': 'Badge 11111'
                        }
                    ]
                },
                {
                    'involved_type': 'police witnesses',
                    'officers': [
                        {
                            'id': 3,
                            'abbr_name': 'J. Ipsum',
                            'extra_info': 'Badge 33333'
                        },
                        {
                            'id': 2,
                            'abbr_name': 'R. Piwinicki',
                            'extra_info': 'Badge 22222'
                        }
                    ]
                }
            ],
            'documents': [
                {
                    'title': 'CR document',
                    'url': 'http://cr-document.com/'
                }
            ]
        })

    def test_retrieve_no_match(self):
        response = self.client.get(reverse('api-v2:cr-detail', kwargs={'pk': 321}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_request_document(self):
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

    def test_request_same_document_twice(self):
        allegation = AllegationFactory(crid='112233')
        self.client.post(
            reverse('api-v2:cr-request-document', kwargs={'pk': allegation.crid}),
            {'email': 'valid_email@example.com'}
        )

        response2 = self.client.post(
            reverse('api-v2:cr-request-document', kwargs={'pk': allegation.crid}),
            {'email': 'valid_email@example.com'}
        )
        expect(response2.status_code).to.eq(status.HTTP_200_OK)
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
                                       incident_date=datetime(2002, 2, 28),
                                       summary='Summary')
        category = AllegationCategoryFactory(category='Use of Force')
        OfficerAllegationFactory(allegation=allegation,
                                 allegation_category=category)
        self.refresh_index()
        response = self.client.get(reverse('api-v2:cr-complaint-summaries'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([{
            'crid': '11',
            'category_names': ['Use of Force'],
            'incident_date': '2002-02-28',
            'summary': 'Summary'
        }])
