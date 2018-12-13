from datetime import datetime

from django.core import management
from django.test import TestCase, override_settings

import pytz
from mock import patch, call
from robber import expect

from data.factories import (
    OfficerFactory, OfficerAllegationFactory, AttachmentRequestFactory,
    AllegationFactory, InvestigatorAllegationFactory, InvestigatorFactory
)
from trr.factories import TRRFactory, TRRAttachmentRequestFactory
from data.models import AttachmentRequest
from trr.models import TRRAttachmentRequest


class UpdateDocumentsCommandTestCase(TestCase):
    @override_settings(AIRTABLE_CPD_AGENCY_ID='CPD_AGENCY_ID', AIRTABLE_COPA_AGENCY_ID='COPA_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_document_requests(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'airtable_id'}

        allegation123 = AllegationFactory(crid='123', incident_date=datetime(2010, 1, 1, tzinfo=pytz.utc))
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation123, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation123, officer=officer_2)
        investigator = InvestigatorFactory(officer=officer_1)
        InvestigatorAllegationFactory(allegation=allegation123, investigator=investigator)
        AttachmentRequestFactory(
            allegation=allegation123,
            email='requester1@example.com',
            airtable_id='')
        AttachmentRequestFactory(
            allegation=allegation123,
            email='requester2@example.com',
            airtable_id='cr2222')

        allegation456 = AllegationFactory(crid='456', incident_date=datetime(2010, 1, 1, tzinfo=pytz.utc))
        officer_3 = OfficerFactory(id=3, first_name='Marry', last_name='Jane')
        officer_4 = OfficerFactory(id=4, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation456, officer=officer_3)
        OfficerAllegationFactory(allegation=allegation456, officer=officer_4)
        AttachmentRequestFactory(
            allegation=allegation456,
            email='requester3@example.com',
            airtable_id='')
        AttachmentRequestFactory(
            allegation=allegation456,
            email='requester4@example.com',
            airtable_id='cr4444')

        trr = TRRFactory(id='123456', officer=officer_1)
        TRRAttachmentRequestFactory(
            trr=trr,
            email='requester@example1.com',
            airtable_id='')
        TRRAttachmentRequestFactory(
            trr=trr,
            email='requester@example2.com',
            airtable_id='trr2222')

        expect(AttachmentRequest.objects.filter(airtable_id='').count()).to.eq(2)
        expect(TRRAttachmentRequest.objects.filter(airtable_id='').count()).to.eq(1)

        management.call_command('upload_document_requests')

        expected_calls = [
            call({
                'Explanation': 'Officers: John Henry(ID 2), Marry Jane(ID 1)',
                'Project': [
                    'CPDP'
                ],
                'Agency': ['CPD_AGENCY_ID'],
                'Requested For': 'CR 123',
                'Requestor': [
                    {
                        'id': 'usrGiZFcyZ6wHTYWd',
                        'email': 'rajiv@invisibleinstitute.com',
                        'name': 'Rajiv Sinclair'
                    }
                ]
            }),
            call({
                'Explanation': 'Officers: John Henry(ID 4), Marry Jane(ID 3)',
                'Project': [
                    'CPDP'
                ],
                'Agency': ['COPA_AGENCY_ID'],
                'Requested For': 'CR 456',
                'Requestor': [
                    {
                        'id': 'usrGiZFcyZ6wHTYWd',
                        'email': 'rajiv@invisibleinstitute.com',
                        'name': 'Rajiv Sinclair'
                    }
                ]
            }),
            call({
                'Explanation':  'Officer: Marry Jane(ID 1)',
                'Project': [
                  'CPDP'
                ],
                'Agency': [],
                'Requested For': 'TRR 123456',
                'Requestor': [
                    {
                        'id': 'usrGiZFcyZ6wHTYWd',
                        'email': 'rajiv@invisibleinstitute.com',
                        'name': 'Rajiv Sinclair'
                    }
                ]
            })
        ]

        airtable_mock.insert.assert_has_calls(expected_calls, any_order=True)

        expect(AttachmentRequest.objects.filter(airtable_id='').count()).to.eq(0)
        expect(TRRAttachmentRequest.objects.filter(airtable_id='').count()).to.eq(0)
