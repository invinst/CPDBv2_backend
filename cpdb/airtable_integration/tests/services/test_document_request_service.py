from django.test.testcases import TestCase

from mock import patch, call, Mock
from robber import expect
from requests.exceptions import HTTPError

from config.settings.common import AIRTABLE_PROJECT_KEY, AIRTABLE_TABLE_NAME
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
)
from trr.factories import TRRAttachmentRequestFactory, TRRFactory


class DocumentRequestServiceTestCase(TestCase):
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_cr_attachment_request_to_foia_with_cpd(self, airtable_mock):
        allegation = AllegationFactory(crid='123456')
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
            'Request Desc': 'CR 123456(investigated by CPD)',
            'Requestor': [
              {
                'id': 'usrVdJCqxgnDTNRFW',
                'email': 'andrew@invisibleinstitute.com',
                'name': 'Andrew Fan'
              },
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ]
        }

        expect(attachment_request.added_to_foia_airtable).to.be.false()

        CRRequestAirTableUploader.upload()
        attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.added_to_foia_airtable).to.be.true()

    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_cr_attachment_request_to_foia_with_copa(self, airtable_mock):
        allegation = AllegationFactory(crid='123456')
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
            'Request Desc': 'CR 123456(investigated by COPA)',
            'Requestor': [
              {
                'id': 'usrVdJCqxgnDTNRFW',
                'email': 'andrew@invisibleinstitute.com',
                'name': 'Andrew Fan'
              },
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ]
        }

        expect(attachment_request.added_to_foia_airtable).to.be.false()

        CRRequestAirTableUploader.upload()
        attachment_request.refresh_from_db()

        airtable_mock.insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.added_to_foia_airtable).to.be.true()

    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_trr_attachment_request_to_foia_with_copa(self, airtable_mock):
        officer = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        trr = TRRFactory(id='123456', officer=officer)
        attachment_request = TRRAttachmentRequestFactory(trr=trr, email='requester@example.com')

        expected_airtable_data = {
            'Explanation':  'Officer: Marry Jane(ID 1)',
            'Project': [
              'CPDP'
            ],
            'Request Desc': 'TRR 123456',
            'Requestor': [
              {
                'id': 'usrVdJCqxgnDTNRFW',
                'email': 'andrew@invisibleinstitute.com',
                'name': 'Andrew Fan'
              },
              {
                'id': 'usrGiZFcyZ6wHTYWd',
                'email': 'rajiv@invisibleinstitute.com',
                'name': 'Rajiv Sinclair'
              }
            ]
        }

        expect(attachment_request.added_to_foia_airtable).to.be.false()

        TRRRequestAirTableUploader.upload()
        attachment_request.refresh_from_db()

        AirTableUploader._get_foia_airtable().insert.assert_called_with(expected_airtable_data)
        expect(attachment_request.added_to_foia_airtable).to.be.true()

    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_AirTableUploader_raise_NotImplementedError(self, _):
        allegation123 = AllegationFactory(crid='123')
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation123, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation123, officer=officer_2)
        investigator = InvestigatorFactory(officer=officer_1)
        InvestigatorAllegationFactory(allegation=allegation123, investigator=investigator)
        cr_request_1 = AttachmentRequestFactory(
            allegation=allegation123,
            email='requester1@example.com',
            added_to_foia_airtable=False)

        allegation456 = AllegationFactory(crid='456')
        officer_3 = OfficerFactory(id=3, first_name='Marry', last_name='Jane')
        officer_4 = OfficerFactory(id=4, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation456, officer=officer_3)
        OfficerAllegationFactory(allegation=allegation456, officer=officer_4)
        cr_request_2 = AttachmentRequestFactory(
            allegation=allegation456,
            email='requester2@example.com',
            added_to_foia_airtable=False)

        expect(AirTableUploader.upload).to.throw(NotImplementedError)

        with patch(
            'airtable_integration.services.document_request_service.AirTableUploader._get_uploaded_objects',
            return_value=[cr_request_1, cr_request_2]
        ):
            expect(AirTableUploader.upload).to.throw(NotImplementedError)

            with patch(
                'airtable_integration.services.document_request_service.'
                'AirTableUploader._build_explanation_and_request_desc',
                return_value=('', '')
            ):
                expect(AirTableUploader.upload).to.throw(NotImplementedError)

                with patch(
                    'airtable_integration.services.document_request_service.'
                    'AirTableUploader._post_handle'
                ):
                    AirTableUploader.upload()

    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_Airtable_insert_raise_HTTPError(self, airtable_mock):
        AirTableUploader._get_foia_airtable().insert = Mock(side_effect=[True, HTTPError])

        allegation123 = AllegationFactory(crid='123')
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation123, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation123, officer=officer_2)
        investigator = InvestigatorFactory(officer=officer_1)
        InvestigatorAllegationFactory(allegation=allegation123, investigator=investigator)
        attachment_request_1 = AttachmentRequestFactory(allegation=allegation123, email='requester1@example.com')

        allegation456 = AllegationFactory(crid='456')
        officer_3 = OfficerFactory(id=3, first_name='Marry', last_name='Jane')
        officer_4 = OfficerFactory(id=4, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation456, officer=officer_3)
        OfficerAllegationFactory(allegation=allegation456, officer=officer_4)
        attachment_request_2 = AttachmentRequestFactory(allegation=allegation456, email='requester2@example.com')

        expect(attachment_request_1.added_to_foia_airtable).to.be.false()
        expect(attachment_request_2.added_to_foia_airtable).to.be.false()

        CRRequestAirTableUploader.upload()
        attachment_request_1.refresh_from_db()
        attachment_request_2.refresh_from_db()

        expected_calls = [
            call({
                'Explanation': 'Officers: John Henry(ID 2), Marry Jane(ID 1)',
                'Project': [
                    'CPDP'
                ],
                'Request Desc': 'CR 123(investigated by CPD)',
                'Requestor': [
                    {
                        'id': 'usrVdJCqxgnDTNRFW',
                        'email': 'andrew@invisibleinstitute.com',
                        'name': 'Andrew Fan'
                    },
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
                'Request Desc': 'CR 456(investigated by COPA)',
                'Requestor': [
                    {
                        'id': 'usrVdJCqxgnDTNRFW',
                        'email': 'andrew@invisibleinstitute.com',
                        'name': 'Andrew Fan'
                    },
                    {
                        'id': 'usrGiZFcyZ6wHTYWd',
                        'email': 'rajiv@invisibleinstitute.com',
                        'name': 'Rajiv Sinclair'
                    }
                ]
            })
        ]
        airtable_mock.insert.assert_has_calls(expected_calls, any_order=True)

        expect(attachment_request_1.added_to_foia_airtable).to.be.true()
        expect(attachment_request_2.added_to_foia_airtable).to.be.false()

    @patch('airtable_integration.services.document_request_service.Airtable')
    def test_AirTableUploader_lazy_evaluate_airtable(self, airtable_cls_mock):
        expect(AirTableUploader._lazy_airtable).to.be.none()

        first_aitable = AirTableUploader._get_foia_airtable()
        second_aitable = AirTableUploader._get_foia_airtable()

        airtable_cls_mock.assert_called_once_with(AIRTABLE_PROJECT_KEY, AIRTABLE_TABLE_NAME)
        expect(first_aitable).to.be.equal(second_aitable)
