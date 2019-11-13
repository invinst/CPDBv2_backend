from requests import Session, RequestException
from urllib3.exceptions import HTTPError

from django.test import TestCase

from mock import patch, Mock
from robber import expect

from data.constants import AttachmentSourceType
from data.factories import AttachmentFileFactory
from data.models import AttachmentFile
from document_cloud.documentcloud_session import DocumentCloudSession


class DocumentCloudSessionTestCase(TestCase):
    def setUp(self):
        self.logger = Mock()

    def test_init_with_logger(self):
        session = DocumentCloudSession(self.logger)
        expect(session.logger).to.eq(self.logger)
        expect(session).to.be.instanceof(Session)

    @patch('document_cloud.documentcloud_session.DocumentCloudSession.post', return_value=Mock(status_code=200))
    @patch('document_cloud.documentcloud_session.DocumentCloudSession.close', return_value=Mock(status_code=200))
    def test_enter_and_exit(self, close_mock, post_mock):
        session = DocumentCloudSession(self.logger)

        with session as s:
            expect(s).to.eq(session)
            expect(post_mock).to.be.called_with(
                'https://www.documentcloud.org/login',
                {'email': 'DOCUMENTCLOUD_USER', 'password': 'DOCUMENTCLOUD_PASSWORD'}
            )

        expect(close_mock).to.be.called()

    @patch('document_cloud.documentcloud_session.DocumentCloudSession.post', side_effect=HTTPError('Invalid request'))
    def test_login_exception(self, _):
        def test_func():
            with DocumentCloudSession(self.logger):
                pass

        expect(test_func).to.be.to.throw(HTTPError)

    @patch(
        'document_cloud.documentcloud_session.DocumentCloudSession.post',
        return_value=Mock(status_code=401, json=Mock(return_value='Unauthorized'))
    )
    def test_login_failure(self, _):
        def test_func():
            with DocumentCloudSession(self.logger):
                pass

        expect(test_func).to.be.to.throw(RequestException)

    @patch('document_cloud.documentcloud_session.DocumentCloudSession.post', return_value=Mock(status_code=200))
    def test_request_reprocess_text_success(self, post_mock):
        with DocumentCloudSession(self.logger) as session:
            requested = session._request_reprocess_text('documentcloud_id')

            expect(post_mock).to.be.called_with(
                'https://www.documentcloud.org/documents/documentcloud_id/reprocess_text',
                headers={
                    'x-requested-with': 'XMLHttpRequest',
                    'accept': 'application/json, text/javascript, */*; q=0.01'
                }
            )
            expect(self.logger.info).to.be.called_with('Reprocessing text with id documentcloud_id success')
            expect(requested).to.be.true()

    @patch(
        'document_cloud.documentcloud_session.DocumentCloudSession.post',
        return_value=Mock(status_code=404, json=Mock(return_value='Document does not exist'))
    )
    def test_request_reprocess_text_failure(self, post_mock):
        session = DocumentCloudSession(self.logger)
        requested = session._request_reprocess_text('not_exist_documentcloud_id')

        expect(post_mock).to.be.called_with(
            'https://www.documentcloud.org/documents/not_exist_documentcloud_id/reprocess_text',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'accept': 'application/json, text/javascript, */*; q=0.01'
            }
        )
        expect(self.logger.warn).to.be.called_with(
            'Reprocessing text not_exist_documentcloud_id failed with status code 404: Document does not exist'
        )
        expect(requested).to.be.true()

    @patch('document_cloud.documentcloud_session.DocumentCloudSession.post', side_effect=HTTPError('Invalid request'))
    def test_request_reprocess_text_exception(self, post_mock):
        session = DocumentCloudSession(self.logger)
        requested = session._request_reprocess_text('exception_documentcloud_id')

        expect(post_mock).to.be.called_with(
            'https://www.documentcloud.org/documents/exception_documentcloud_id/reprocess_text',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'accept': 'application/json, text/javascript, */*; q=0.01'
            }
        )
        expect(self.logger.warn).to.be.called_with(
            'Exception when sending reprocess exception_documentcloud_id request: Invalid request'
        )
        expect(requested).to.be.false()

    @patch('document_cloud.documentcloud_session.time')
    @patch('document_cloud.documentcloud_session.DocumentCloudSession.post', return_value=Mock(status_code=200))
    def test_request_reprocess_missing_text_documents_with_delay(self, post_mock, time_mock):
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
            external_id='SUMMARY_REPORTS_COPA_DOCUMENTCLOUD_empty_text_id',
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
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

        with DocumentCloudSession(self.logger) as session:
            session.request_reprocess_missing_text_documents_with_delay()

        expect(post_mock).to.be.any_call(
            'https://www.documentcloud.org/login',
            {'email': 'DOCUMENTCLOUD_USER', 'password': 'DOCUMENTCLOUD_PASSWORD'}
        )

        expect(post_mock).to.be.any_call(
            'https://www.documentcloud.org/documents/DOCUMENTCLOUD_empty_text_id/reprocess_text',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'accept': 'application/json, text/javascript, */*; q=0.01'
            }
        )
        expect(self.logger.info).to.be.any_call(
            'Reprocessing text with id DOCUMENTCLOUD_empty_text_id success'
        )

        expect(post_mock).to.be.any_call(
            'https://www.documentcloud.org/documents/PORTAL_COPA_DOCUMENTCLOUD_empty_text_id/reprocess_text',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'accept': 'application/json, text/javascript, */*; q=0.01'
            }
        )
        expect(self.logger.info).to.be.any_call(
            'Reprocessing text with id PORTAL_COPA_DOCUMENTCLOUD_empty_text_id success'
        )

        expect(post_mock).to.be.any_call(
            'https://www.documentcloud.org/documents/SUMMARY_'
            'REPORTS_COPA_DOCUMENTCLOUD_empty_text_id/reprocess_text',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'accept': 'application/json, text/javascript, */*; q=0.01'
            }
        )
        expect(self.logger.info).to.be.any_call(
            'Reprocessing text with id SUMMARY_REPORTS_COPA_DOCUMENTCLOUD_empty_text_id success'
        )

        expect(time_mock.sleep.call_count).to.equal(3)

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
    @patch('document_cloud.documentcloud_session.DocumentCloudSession.post', side_effect=HTTPError('Invalid request'))
    def test_request_reprocess_missing_text_not_update_count_when_cannot_sending_requests(self, _, __):
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

        session = DocumentCloudSession(self.logger)
        session.request_reprocess_missing_text_documents_with_delay()

        expect(
            AttachmentFile.objects.get(external_id='DOCUMENTCLOUD_empty_text_id').reprocess_text_count
        ).to.equal(0)
        expect(
            AttachmentFile.objects.get(external_id='PORTAL_COPA_DOCUMENTCLOUD_empty_text_id').reprocess_text_count
        ).to.equal(1)
