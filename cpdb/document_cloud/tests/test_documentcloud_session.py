from data.constants import AttachmentSourceType
from data.factories import AttachmentFileFactory
from data.models import AttachmentFile
from django.test import TestCase
from document_cloud.documentcloud_session import DocumentCloudSession
from mock import Mock, patch
from requests import Session
from robber import expect
from urllib3.exceptions import HTTPError


class DocumentCloudSessionTestCase(TestCase):
    def setUp(self):
        self.log_func = Mock()

    @patch('document_cloud.documentcloud_session.DocumentCloudSession.post', return_value=Mock(status_code=200))
    @patch('document_cloud.documentcloud_session.DocumentCloudSession.close', return_value=Mock(status_code=200))
    def test_login_while_init(self, close_mock, post_mock):
        with DocumentCloudSession(self.log_func) as session:
            expect(post_mock).to.be.called_with(
                'https://www.documentcloud.org/login',
                {'email': '', 'password': ''}
            )
            expect(session.log_func).to.eq(self.log_func)
            expect(session).to.be.instanceof(Session)

        expect(close_mock).to.be.called()

    @patch('document_cloud.documentcloud_session.DocumentCloudSession.post', side_effect=HTTPError('Invalid request'))
    def test_login_exception(self, _):
        expect(lambda: DocumentCloudSession(self.log_func)).to.be.to.throw(HTTPError)

    # @patch(
    #     'document_cloud.documentcloud_session.DocumentCloudSession.post',
    #     return_value=Mock(status_code=401, json=Mock(return_value='Unauthorized'))
    # )
    # def test_login_failure(self, _):
    #     expect(lambda: DocumentCloudSession(self.log_func)).to.be.to.throw(RequestException)
    #     expect(self.log_func).to.be.called_with('[ERROR] Cannot login to document cloud to reprocessing text')

    @patch('document_cloud.documentcloud_session.DocumentCloudSession.post', return_value=Mock(status_code=200))
    def test_request_reprocess_text_success(self, post_mock):
        document = AttachmentFile(
            external_id='documentcloud_id',
            url='https://www.documentcloud.org/documents/documentcloud_id-CRID-234-CR.html'
        )

        with DocumentCloudSession(self.log_func) as session:
            requested, success = session._request_reprocess_text(document)

            expect(post_mock).to.be.called_with(
                'https://www.documentcloud.org/api/documents/documentcloud_id/process',
                headers={
                    'x-requested-with': 'XMLHttpRequest',
                    'accept': 'application/json, text/javascript, */*; q=0.01'
                }
            )
            expect(self.log_func).to.be.called_with(
                '[SUCCESS] Reprocessing text https://www.documentcloud.org/documents/documentcloud_id-CRID-234-CR.html'
            )
            expect(requested).to.be.true()
            expect(success).to.be.true()

    def test_request_reprocess_text_failure(self):
        document = AttachmentFile(
            external_id='not_exist_documentcloud_id',
            url='https://www.documentcloud.org/documents/not_exist_documentcloud_id-CRID-234-CR.html'
        )

        with patch(
            'document_cloud.documentcloud_session.DocumentCloudSession.post',
            return_value=Mock(status_code=200)
        ):
            session = DocumentCloudSession(self.log_func)

        with patch(
            'document_cloud.documentcloud_session.DocumentCloudSession.post',
            return_value=Mock(status_code=404, json=Mock(return_value='Document does not exist'))
        ) as post_mock:
            requested, success = session._request_reprocess_text(document)

            expect(post_mock).to.be.called_with(
                'https://www.documentcloud.org/api/documents/not_exist_documentcloud_id/process',
                headers={
                    'x-requested-with': 'XMLHttpRequest',
                    'accept': 'application/json, text/javascript, */*; q=0.01'
                }
            )
            expect(self.log_func).to.be.called_with(
                '[FAIL] Reprocessing text'
                ' https://www.documentcloud.org/documents/not_exist_documentcloud_id-CRID-234-CR.html'
                ' failed with status code 404: Document does not exist'
            )
            expect(requested).to.be.true()
            expect(success).to.be.false()

    def test_request_reprocess_text_exception(self):
        document = AttachmentFile(
            external_id='exception_documentcloud_id',
            url='https://www.documentcloud.org/documents/exception_documentcloud_id-CRID-234-CR.html'
        )

        with patch(
            'document_cloud.documentcloud_session.DocumentCloudSession.post',
            return_value=Mock(status_code=200)
        ):
            session = DocumentCloudSession(self.log_func)

        with patch(
            'document_cloud.documentcloud_session.DocumentCloudSession.post',
            side_effect=HTTPError('Invalid request')
        ) as post_mock:
            requested, success = session._request_reprocess_text(document)

            expect(post_mock).to.be.called_with(
                'https://www.documentcloud.org/api/documents/exception_documentcloud_id/process',
                headers={
                    'x-requested-with': 'XMLHttpRequest',
                    'accept': 'application/json, text/javascript, */*; q=0.01'
                }
            )
            expect(self.log_func).to.be.called_with(
                '[ERROR] when sending reprocess request for '
                'https://www.documentcloud.org/documents/exception_documentcloud_id-CRID-234-CR.html: Invalid request'
            )
            expect(requested).to.be.false()
            expect(success).to.be.false()

    @patch('document_cloud.documentcloud_session.time')
    @patch('document_cloud.documentcloud_session.DocumentCloudSession.post', return_value=Mock(status_code=200))
    def test_request_reprocess_missing_text_documents(self, post_mock, time_mock):
        AttachmentFileFactory(
            file_type='document',
            text_content='',
            external_id='DOCUMENTCLOUD_empty_text_id',
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            url='https://www.documentcloud.org/documents/DOCUMENTCLOUD_empty_text_id-CRID-234-CR.html'
        )
        AttachmentFileFactory(
            file_type='document',
            text_content='',
            external_id='PORTAL_COPA_DOCUMENTCLOUD_empty_text_id',
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            url='https://www.documentcloud.org/documents/PORTAL_COPA_DOCUMENTCLOUD_empty_text_id-CRID-234-CR.html',
            reprocess_text_count=1,
        )
        AttachmentFileFactory(
            file_type='document',
            text_content='',
            external_id='SUMMARY_REPORTS_COPA_DOCUMENTCLOUD_empty_text_id',
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            url='https://www.documentcloud.org/documents/SUMMARY_COPA_DOCUMENTCLOUD_empty_text_id-CRID-234-CR.html',
            reprocess_text_count=2,
        )
        AttachmentFileFactory(
            file_type='audio',
            text_content='',
            external_id='audio_id',
            source_type=AttachmentSourceType.PORTAL_COPA,
        )
        AttachmentFileFactory(
            file_type='video',
            text_content='',
            external_id='vimeo_id',
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA,
        )
        AttachmentFileFactory(
            file_type='document',
            text_content='Some content',
            external_id='DOCUMENTCLOUD_has_text_id',
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
        )
        AttachmentFileFactory(
            file_type='document',
            text_content='',
            external_id='DOCUMENTCLOUD_tries_enough_id',
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            reprocess_text_count=3,
        )

        with DocumentCloudSession(self.log_func) as session:
            session.request_reprocess_missing_text_documents()

        expect(post_mock).to.be.any_call(
            'https://www.documentcloud.org/login',
            {'email': '', 'password': ''}
        )

        expect(post_mock).to.be.any_call(
            'https://www.documentcloud.org/api/documents/DOCUMENTCLOUD_empty_text_id/process',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'accept': 'application/json, text/javascript, */*; q=0.01'
            }
        )
        expect(self.log_func).to.be.any_call(
            '[SUCCESS] Reprocessing text '
            'https://www.documentcloud.org/documents/DOCUMENTCLOUD_empty_text_id-CRID-234-CR.html'
        )

        expect(post_mock).to.be.any_call(
            'https://www.documentcloud.org/api/documents/PORTAL_COPA_DOCUMENTCLOUD_empty_text_id/process',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'accept': 'application/json, text/javascript, */*; q=0.01'
            }
        )
        expect(self.log_func).to.be.any_call(
            '[SUCCESS] Reprocessing text '
            'https://www.documentcloud.org/documents/PORTAL_COPA_DOCUMENTCLOUD_empty_text_id-CRID-234-CR.html'
        )

        expect(post_mock).to.be.any_call(
            'https://www.documentcloud.org/api/documents/SUMMARY_'
            'REPORTS_COPA_DOCUMENTCLOUD_empty_text_id/process',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'accept': 'application/json, text/javascript, */*; q=0.01'
            }
        )
        expect(self.log_func).to.be.any_call(
            '[SUCCESS] Reprocessing text '
            'https://www.documentcloud.org/documents/SUMMARY_COPA_DOCUMENTCLOUD_empty_text_id-CRID-234-CR.html'
        )

        expect(self.log_func).to.be.any_call(
            'Sent reprocessing text requests: 3 success, 0 failure, 1 skipped for 4 no-text documents'
        )

        expect(time_mock.sleep.call_count).to.equal(3)
        expect(time_mock.sleep).to.be.called_with(0.01)

        expect(
            AttachmentFile.objects.get(external_id='DOCUMENTCLOUD_empty_text_id').reprocess_text_count
        ).to.equal(1)
        expect(
            AttachmentFile.objects.get(external_id='PORTAL_COPA_DOCUMENTCLOUD_empty_text_id').reprocess_text_count
        ).to.equal(2)
        expect(
            AttachmentFile.objects.get(
                external_id='SUMMARY_REPORTS_COPA_DOCUMENTCLOUD_empty_text_id'
            ).reprocess_text_count
        ).to.equal(3)
        expect(
            AttachmentFile.objects.get(external_id='audio_id').reprocess_text_count
        ).to.equal(0)
        expect(
            AttachmentFile.objects.get(external_id='vimeo_id').reprocess_text_count
        ).to.equal(0)
        expect(
            AttachmentFile.objects.get(external_id='DOCUMENTCLOUD_has_text_id').reprocess_text_count
        ).to.equal(0)
        expect(
            AttachmentFile.objects.get(external_id='DOCUMENTCLOUD_tries_enough_id').reprocess_text_count
        ).to.equal(3)

    @patch('document_cloud.documentcloud_session.time')
    def test_request_reprocess_missing_text_not_update_count_when_cannot_sending_requests(self, _):
        AttachmentFileFactory(
            file_type='document',
            text_content='',
            external_id='DOCUMENTCLOUD_empty_text_id',
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
        )
        AttachmentFileFactory(
            file_type='document',
            text_content='',
            external_id='PORTAL_COPA_DOCUMENTCLOUD_empty_text_id',
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            reprocess_text_count=1,
        )

        AttachmentFileFactory(
            file_type='document',
            text_content='',
            external_id='DOCUMENTCLOUD_tries_enough_id',
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            reprocess_text_count=3,
        )

        with patch(
            'document_cloud.documentcloud_session.DocumentCloudSession.post',
            return_value=Mock(status_code=200)
        ):
            session = DocumentCloudSession(self.log_func)

        with patch(
            'document_cloud.documentcloud_session.DocumentCloudSession.post',
            side_effect=HTTPError('Invalid request')
        ):
            session.request_reprocess_missing_text_documents()

        expect(self.log_func).to.be.any_call(
            'Sent reprocessing text requests: 0 success, 2 failure, 1 skipped for 3 no-text documents'
        )

        expect(
            AttachmentFile.objects.get(external_id='DOCUMENTCLOUD_empty_text_id').reprocess_text_count
        ).to.equal(0)
        expect(
            AttachmentFile.objects.get(external_id='PORTAL_COPA_DOCUMENTCLOUD_empty_text_id').reprocess_text_count
        ).to.equal(1)
        expect(
            AttachmentFile.objects.get(external_id='DOCUMENTCLOUD_tries_enough_id').reprocess_text_count
        ).to.equal(3)

    @patch('document_cloud.documentcloud_session.time')
    def test_request_reprocess_missing_text_update_count_even_if_status_code_is_not_200(self, _):
        AttachmentFileFactory(
            file_type='document',
            text_content='',
            external_id='DOCUMENTCLOUD_empty_text_id',
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
        )
        AttachmentFileFactory(
            file_type='document',
            text_content='',
            external_id='PORTAL_COPA_DOCUMENTCLOUD_empty_text_id',
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            reprocess_text_count=1,
        )

        AttachmentFileFactory(
            file_type='document',
            text_content='',
            external_id='DOCUMENTCLOUD_tries_enough_id',
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            reprocess_text_count=3,
        )

        with patch(
            'document_cloud.documentcloud_session.DocumentCloudSession.post',
            return_value=Mock(status_code=200)
        ):
            session = DocumentCloudSession(self.log_func)

        with patch(
            'document_cloud.documentcloud_session.DocumentCloudSession.post',
            return_value=Mock(status_code=404, json=Mock(return_value=''))
        ):
            session.request_reprocess_missing_text_documents()

        expect(self.log_func).to.be.any_call(
            'Sent reprocessing text requests: 0 success, 2 failure, 1 skipped for 3 no-text documents'
        )

        expect(
            AttachmentFile.objects.get(external_id='DOCUMENTCLOUD_empty_text_id').reprocess_text_count
        ).to.equal(1)
        expect(
            AttachmentFile.objects.get(external_id='PORTAL_COPA_DOCUMENTCLOUD_empty_text_id').reprocess_text_count
        ).to.equal(2)
        expect(
            AttachmentFile.objects.get(external_id='DOCUMENTCLOUD_tries_enough_id').reprocess_text_count
        ).to.equal(3)
