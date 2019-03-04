from datetime import datetime

from django.test import override_settings
from django.test.testcases import TestCase
from django.conf import settings

import pytz
from mock import patch, call, Mock
from robber import expect
from requests.exceptions import HTTPError
from freezegun import freeze_time

from airtable_integration.services.document_request_service import (
    CRRequestAirTableUploader,
    TRRRequestAirTableUploader,
    AirTableUploader
)
from data.factories import (
    AllegationFactory,
    AttachmentRequestFactory,
    OfficerAllegationFactory,
    OfficerFactory,
    InvestigatorAllegationFactory,
    InvestigatorFactory,
    OfficerBadgeNumberFactory)
from trr.factories import TRRAttachmentRequestFactory, TRRFactory


class DocumentRequestServiceTestCase(TestCase):
    @override_settings(AIRTABLE_CPD_AGENCY_ID='CPD_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_cr_attachment_request_to_foia_with_cpd(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'some_airtable_record_id'}

        allegation = AllegationFactory(crid='123456', incident_date=datetime(2005, 1, 1, tzinfo=pytz.utc))
        attachment_request = AttachmentRequestFactory(allegation=allegation, email='requester@example.com')
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)
        investigator = InvestigatorFactory(officer=officer_1)
        InvestigatorAllegationFactory(allegation=allegation, investigator=investigator)

        expected_airtable_data = {
            'Explanation':  'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
              'CPDP'
            ],
            'Agency': ['CPD_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        expect(attachment_request.airtable_id).to.be.eq('')

        CRRequestAirTableUploader.upload()
        attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('some_airtable_record_id')

    @override_settings(AIRTABLE_CPD_AGENCY_ID='CPD_AGENCY_ID', TIME_ZONE='UTC')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_cr_attachment_request_to_foia_with_cpd_for_pre_2006(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'some_airtable_record_id'}

        allegation = AllegationFactory(crid='123456', incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc))
        with freeze_time(datetime(2017, 3, 3, 12, 0, 1, tzinfo=pytz.utc)):
            attachment_request = AttachmentRequestFactory(allegation=allegation, email='requester@example.com')
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)

        expected_airtable_data = {
            'Explanation':  'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
              'CPDP'
            ],
            'Agency': ['CPD_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        expect(attachment_request.airtable_id).to.be.eq('')
        expect(attachment_request.updated_at).to.eq(datetime(2017, 3, 3, 12, 0, 1, tzinfo=pytz.utc))

        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            CRRequestAirTableUploader.upload()
            attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('some_airtable_record_id')
        expect(attachment_request.updated_at).to.eq(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc))

    @override_settings(AIRTABLE_COPA_AGENCY_ID='COPA_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_cr_attachment_request_to_foia_with_cpd_for_pre_2006_but_no_incident_date(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'some_airtable_record_id'}

        allegation = AllegationFactory(crid='123456', incident_date=None)
        attachment_request = AttachmentRequestFactory(allegation=allegation, email='requester@example.com')
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)

        expected_airtable_data = {
            'Explanation':  'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
              'CPDP'
            ],
            'Agency': ['COPA_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        expect(attachment_request.airtable_id).to.be.eq('')

        CRRequestAirTableUploader.upload()
        attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('some_airtable_record_id')

    @patch('django.conf.settings.AIRTABLE_CPD_AGENCY_ID', 'CPD_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_cr_attachment_request_to_foia_with_cpd_after_2006_has_current_star(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'some_airtable_record_id'}

        allegation = AllegationFactory(crid='123456', incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))
        attachment_request = AttachmentRequestFactory(allegation=allegation, email='requester@example.com')
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        InvestigatorAllegationFactory(allegation=allegation, current_star='123456')
        InvestigatorAllegationFactory(allegation=allegation, current_star='456789')
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)

        expected_airtable_data = {
            'Explanation': 'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
                'CPDP'
            ],
            'Agency': ['CPD_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
                {
                    'id': 'usrGiZFcyZ6wHTYWd',
                    'email': 'rajiv@invisibleinstitute.com',
                    'name': 'Rajiv Sinclair'
                }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        CRRequestAirTableUploader.upload()
        attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('some_airtable_record_id')

    @patch('django.conf.settings.AIRTABLE_CPD_AGENCY_ID', 'CPD_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_cr_attachment_request_to_foia_with_cpd_after_2006_has_badge_number(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'some_airtable_record_id'}

        allegation = AllegationFactory(crid='123456', incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))
        attachment_request = AttachmentRequestFactory(allegation=allegation, email='requester@example.com')
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerBadgeNumberFactory(officer=officer_1, star='12345')
        OfficerBadgeNumberFactory(officer=officer_2, star='56789')
        investigator_1 = InvestigatorFactory(officer=officer_1)
        investigator_2 = InvestigatorFactory(officer=officer_1)
        InvestigatorAllegationFactory(allegation=allegation, current_star=None, investigator=investigator_1)
        InvestigatorAllegationFactory(allegation=allegation, current_star=None, investigator=investigator_2)
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)

        expected_airtable_data = {
            'Explanation': 'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
                'CPDP'
            ],
            'Agency': ['CPD_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
                {
                    'id': 'usrGiZFcyZ6wHTYWd',
                    'email': 'rajiv@invisibleinstitute.com',
                    'name': 'Rajiv Sinclair'
                }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        CRRequestAirTableUploader.upload()
        attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('some_airtable_record_id')

    @patch('django.conf.settings.AIRTABLE_COPA_AGENCY_ID', 'COPA_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_cr_attachment_request_to_foia_with_cpd_after_2006(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'some_airtable_record_id'}

        allegation = AllegationFactory(crid='123456', incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))
        attachment_request = AttachmentRequestFactory(allegation=allegation, email='requester@example.com')
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        InvestigatorAllegationFactory(allegation=allegation, current_star=None)
        InvestigatorAllegationFactory(allegation=allegation, current_star=None)
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)

        expected_airtable_data = {
            'Explanation': 'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
                'CPDP'
            ],
            'Agency': ['COPA_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
                {
                    'id': 'usrGiZFcyZ6wHTYWd',
                    'email': 'rajiv@invisibleinstitute.com',
                    'name': 'Rajiv Sinclair'
                }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        CRRequestAirTableUploader.upload()
        attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('some_airtable_record_id')

    @override_settings(AIRTABLE_COPA_AGENCY_ID='COPA_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_cr_attachment_request_to_foia_with_copa(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'some_airtable_record_id'}

        allegation = AllegationFactory(crid='123456', incident_date=datetime(2010, 1, 1, tzinfo=pytz.utc))
        attachment_request = AttachmentRequestFactory(allegation=allegation, email='requester@example.com')
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)

        expected_airtable_data = {
            'Explanation':  'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
              'CPDP'
            ],
            'Agency': ['COPA_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        expect(attachment_request.airtable_id).to.be.eq('')

        CRRequestAirTableUploader.upload()
        attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('some_airtable_record_id')

    @override_settings(AIRTABLE_COPA_AGENCY_ID='COPA_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_update_cr_attachment_request_to_foia_with_empty_airtable_id(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'airtable_id'}

        allegation = AllegationFactory(crid='123456', incident_date=datetime(2010, 1, 1, tzinfo=pytz.utc))
        attachment_request = AttachmentRequestFactory(
            allegation=allegation,
            email='requester@example.com',
            airtable_id=''
        )
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)

        expected_airtable_data = {
            'Explanation':  'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
              'CPDP'
            ],
            'Agency': ['COPA_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        expect(attachment_request.airtable_id).to.be.eq('')
        CRRequestAirTableUploader.upload(update_all_records=True)
        attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('airtable_id')

    @override_settings(AIRTABLE_COPA_AGENCY_ID='COPA_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_update_cr_attachment_request_to_foia_with_valid_airtable_id(self, airtable_mock):
        airtable_mock.update = Mock(side_effect=[HTTPError('500')])

        allegation = AllegationFactory(crid='123456', incident_date=datetime(2010, 1, 1, tzinfo=pytz.utc))
        attachment_request = AttachmentRequestFactory(
            allegation=allegation,
            email='requester@example.com',
            airtable_id='airtable_id'
        )
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)

        expected_airtable_data = {
            'Explanation':  'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
              'CPDP'
            ],
            'Agency': ['COPA_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        CRRequestAirTableUploader.upload(update_all_records=True)
        attachment_request.refresh_from_db()

        airtable_mock.update.assert_called_with('airtable_id', expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('airtable_id')

    @override_settings(AIRTABLE_COPA_AGENCY_ID='COPA_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_update_cr_attachment_request_to_foia_with_valid_airtable_id_with_error(self, airtable_mock):
        airtable_mock.update.return_value = {'id': 'airtable_id'}

        allegation = AllegationFactory(crid='123456', incident_date=datetime(2010, 1, 1, tzinfo=pytz.utc))
        attachment_request = AttachmentRequestFactory(
            allegation=allegation,
            email='requester@example.com',
            airtable_id='airtable_id'
        )
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)

        expected_airtable_data = {
            'Explanation':  'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
              'CPDP'
            ],
            'Agency': ['COPA_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        CRRequestAirTableUploader.upload(update_all_records=True)
        attachment_request.refresh_from_db()

        airtable_mock.update.assert_called_with('airtable_id', expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('airtable_id')

    @override_settings(AIRTABLE_COPA_AGENCY_ID='COPA_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_update_cr_attachment_request_to_foia_with_invalid_airtable_id(self, airtable_mock):
        airtable_mock.update = Mock(side_effect=[HTTPError('404')])
        airtable_mock.insert.return_value = {'id': 'airtable_id'}

        allegation = AllegationFactory(crid='123456', incident_date=datetime(2010, 1, 1, tzinfo=pytz.utc))
        attachment_request = AttachmentRequestFactory(
            allegation=allegation,
            email='requester@example.com',
            airtable_id='invalid_airtable_id'
        )
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation, officer=officer_2)

        expected_airtable_data = {
            'Explanation':  'Officers: John Henry(ID 2), Marry Jane(ID 1)',
            'Project': [
              'CPDP'
            ],
            'Agency': ['COPA_AGENCY_ID'],
            'Requested For': 'CR 123456',
            'Requestor': [
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        CRRequestAirTableUploader.upload(update_all_records=True)
        attachment_request.refresh_from_db()

        airtable_mock.update.assert_called_with('invalid_airtable_id', expected_airtable_data)
        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('airtable_id')

    @override_settings(TIME_ZONE='UTC')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_trr_attachment_request_to_foia_with_copa(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'some_airtable_record_id'}

        officer = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        trr = TRRFactory(id='123456', officer=officer)
        with freeze_time(datetime(2017, 3, 3, 12, 0, 1, tzinfo=pytz.utc)):
            attachment_request = TRRAttachmentRequestFactory(trr=trr, email='requester@example.com')

        expected_airtable_data = {
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
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        expect(attachment_request.airtable_id).to.be.eq('')
        expect(attachment_request.updated_at).to.eq(datetime(2017, 3, 3, 12, 0, 1, tzinfo=pytz.utc))

        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            TRRRequestAirTableUploader.upload()
            attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('some_airtable_record_id')
        expect(attachment_request.updated_at).to.eq(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc))

    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_update_trr_attachment_request_to_foia_with_valid_airtable_id(self, airtable_mock):
        airtable_mock.update.return_value = {'id': 'airtable_id'}

        officer = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        trr = TRRFactory(id='123456', officer=officer)
        attachment_request = TRRAttachmentRequestFactory(
            trr=trr,
            email='requester@example.com',
            airtable_id='airtable_id'
        )

        expected_airtable_data = {
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
            ],
            'Date requested by user': attachment_request.created_at.strftime(format='%Y-%m-%d')
        }

        TRRRequestAirTableUploader.upload(update_all_records=True)
        attachment_request.refresh_from_db()

        airtable_mock.update.assert_called_with('airtable_id', expected_airtable_data)
        expect(attachment_request.airtable_id).to.be.eq('airtable_id')

    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_AirTableUploader_raise_NotImplementedError(self, airtable_mock):
        airtable_mock.insert.return_value = {'id': 'some_airtable_record_id'}

        allegation123 = AllegationFactory(crid='123', incident_date=datetime(2010, 1, 1, tzinfo=pytz.utc))
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation123, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation123, officer=officer_2)
        investigator = InvestigatorFactory(officer=officer_1)
        InvestigatorAllegationFactory(allegation=allegation123, investigator=investigator)
        cr_request_1 = AttachmentRequestFactory(
            allegation=allegation123,
            email='requester1@example.com',
            airtable_id='')

        allegation456 = AllegationFactory(crid='456')
        officer_3 = OfficerFactory(id=3, first_name='Marry', last_name='Jane')
        officer_4 = OfficerFactory(id=4, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation456, officer=officer_3)
        OfficerAllegationFactory(allegation=allegation456, officer=officer_4)
        cr_request_2 = AttachmentRequestFactory(
            allegation=allegation456,
            email='requester2@example.com',
            airtable_id='')

        expect(AirTableUploader.upload).to.throw(NotImplementedError)

        with patch(
            'airtable_integration.services.document_request_service.AirTableUploader._get_uploaded_objects',
            return_value=[cr_request_1, cr_request_2]
        ):
            expect(AirTableUploader.upload).to.throw(NotImplementedError)

            with patch(
                'airtable_integration.services.document_request_service.'
                'AirTableUploader._build_data',
                return_value=('', '', [])
            ):
                expect(AirTableUploader.upload).to.throw(NotImplementedError)

                with patch(
                    'airtable_integration.services.document_request_service.'
                    'AirTableUploader._post_handle'
                ):
                    AirTableUploader.upload()

    @override_settings(AIRTABLE_CPD_AGENCY_ID='CPD_AGENCY_ID', AIRTABLE_COPA_AGENCY_ID='COPA_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_Airtable_insert_raise_HTTPError(self, airtable_mock):
        AirTableUploader._get_foia_airtable().insert = Mock(side_effect=[{'id': 'some_airtable_record_id'}, HTTPError])

        allegation123 = AllegationFactory(crid='123', incident_date=datetime(2005, 1, 1, tzinfo=pytz.utc))
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation123, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation123, officer=officer_2)
        investigator = InvestigatorFactory(officer=officer_1)
        InvestigatorAllegationFactory(allegation=allegation123, investigator=investigator)
        attachment_request_1 = AttachmentRequestFactory(allegation=allegation123, email='requester1@example.com')

        allegation456 = AllegationFactory(crid='456', incident_date=datetime(2011, 1, 1, tzinfo=pytz.utc))
        officer_3 = OfficerFactory(id=3, first_name='Marry', last_name='Jane')
        officer_4 = OfficerFactory(id=4, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation456, officer=officer_3)
        OfficerAllegationFactory(allegation=allegation456, officer=officer_4)
        attachment_request_2 = AttachmentRequestFactory(allegation=allegation456, email='requester2@example.com')

        expect(attachment_request_1.airtable_id).to.eq('')
        expect(attachment_request_2.airtable_id).to.eq('')

        CRRequestAirTableUploader.upload()
        attachment_request_1.refresh_from_db()
        attachment_request_2.refresh_from_db()

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
                ],
                'Date requested by user': attachment_request_1.created_at.strftime(format='%Y-%m-%d')
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
                ],
                'Date requested by user': attachment_request_2.created_at.strftime(format='%Y-%m-%d')
            })
        ]
        airtable_mock.insert.assert_has_calls(expected_calls, any_order=True)

        expect(attachment_request_1.airtable_id).to.eq('some_airtable_record_id')
        expect(attachment_request_2.airtable_id).to.eq('')

    @patch('airtable_integration.services.document_request_service.Airtable')
    def test_AirTableUploader_lazy_evaluate_airtable(self, airtable_cls_mock):
        expect(AirTableUploader._lazy_airtable).to.be.none()

        first_aitable = AirTableUploader._get_foia_airtable()
        second_aitable = AirTableUploader._get_foia_airtable()

        airtable_cls_mock.assert_called_once_with(settings.AIRTABLE_PROJECT_KEY, settings.AIRTABLE_TABLE_NAME)
        expect(first_aitable).to.be.equal(second_aitable)
