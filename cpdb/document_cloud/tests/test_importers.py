import logging
import json
import urllib3
from datetime import datetime
from urllib.error import HTTPError

from django.test import TestCase, override_settings
from django.core import management

import pytz
from mock import patch, Mock, MagicMock
from robber import expect
from freezegun import freeze_time

from data.constants import AttachmentSourceType
from data.factories import AllegationFactory, AttachmentFileFactory
from data.models import AttachmentFile
from document_cloud.constants import DOCUMENT_CRAWLER_SUCCESS, DOCUMENT_CRAWLER_FAILED
from document_cloud.factories import DocumentCrawlerFactory
from document_cloud.models import DocumentCrawler
from document_cloud.importers import DocumentCloudAttachmentImporter
from email_service.constants import CR_ATTACHMENT_AVAILABLE
from email_service.factories import EmailTemplateFactory
from shared.tests.utils import create_object


@override_settings(S3_BUCKET_CRAWLER_LOG='crawler_logs_bucket')
class DocumentCloudAttachmentImporterTestCase(TestCase):
    def setUp(self):
        self.logger = logging.getLogger('crawler.update_documents')

    def test_get_full_text(self):
        text_content = """

        something


        something

        """
        cloud_document = create_object({'full_text': text_content.encode('utf8')})
        expect(DocumentCloudAttachmentImporter(self.logger).get_full_text(cloud_document)).to.eq("something\nsomething")

    def test_get_full_text_raise_HTTPError_exception(self):
        class Document(object):
            @property
            def full_text(self):
                raise HTTPError('Testing url', '404', 'Testing error', None, None)

        cloud_document = Document()
        expect(DocumentCloudAttachmentImporter(self.logger).get_full_text(cloud_document)).to.eq('')

    def test_get_full_text_raise_NotImplementedError_exception(self):
        class Document(object):
            @property
            def full_text(self):
                raise NotImplementedError('Testing error')

        cloud_document = Document()
        expect(DocumentCloudAttachmentImporter(self.logger).get_full_text(cloud_document)).to.eq('')

    @patch('shared.attachment_importer.aws')
    def test_create_crawler_log(self, _):
        EmailTemplateFactory(type=CR_ATTACHMENT_AVAILABLE)
        expect(DocumentCrawler.objects.count()).to.eq(0)

        management.call_command('update_documents')

        expect(DocumentCrawler.objects.count()).to.eq(1)

    def test_get_attachment_has_source_type(self):
        allegation = AllegationFactory(crid='123')
        copa_attachment = AttachmentFileFactory(
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            external_id='1'
        )

        document = create_object({
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'documentcloud_id': '1',
        })

        expect(DocumentCloudAttachmentImporter(self.logger).get_attachment(document)).to.be.eq(copa_attachment)

    def test_get_attachment_source_type_empty(self):
        allegation = AllegationFactory(crid='123')
        copa_attachment = AttachmentFileFactory(
            allegation=allegation,
            source_type='',
            external_id='1',
            original_url='https://www.documentcloud.org/documents/1-CRID-123456-CR.html'
        )

        document = create_object({
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'documentcloud_id': '2',
        })

        expect(DocumentCloudAttachmentImporter(self.logger).get_attachment(document)).to.be.eq(copa_attachment)

    def test_get_attachment_return_none(self):
        allegation = AllegationFactory(crid='123')
        AttachmentFileFactory(
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            external_id='1',
            original_url='https://www.documentcloud.org/documents/1-CRID-123456-CR.html'
        )
        AttachmentFileFactory(
            allegation=allegation,
            source_type='',
            external_id='2',
            original_url='wrong_url'
        )

        document = create_object({
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'documentcloud_id': '3',
        })

        expect(DocumentCloudAttachmentImporter(self.logger).get_attachment(document)).to.be.eq(None)

    def test_update_attachment_external_created_at_not_none(self):
        attachment = AttachmentFileFactory(
            url='old_url',
            title='old title',
            preview_image_url='http://web.com/image',
            external_last_updated=datetime(2017, 1, 2, tzinfo=pytz.utc),
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='old tag',
            source_type=AttachmentSourceType.PORTAL_COPA,
            text_content=''
        )
        document = create_object({
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 3, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'full_text': 'text content'.encode('utf8'),
            'pages': 11,
            'access': 'public',
        })

        changed = DocumentCloudAttachmentImporter(self.logger).update_attachment(attachment, document)

        expect(changed).to.be.true()
        expect(attachment.url).to.eq('https://www.documentcloud.org/documents/1-CRID-123456-CR.html')
        expect(attachment.title).to.eq('new title')
        expect(attachment.preview_image_url).to.eq('http://web.com/new-image')
        expect(attachment.external_last_updated).to.eq(datetime(2017, 1, 3, tzinfo=pytz.utc))
        expect(attachment.external_created_at).to.eq(datetime(2017, 1, 2, tzinfo=pytz.utc))
        expect(attachment.tag).to.eq('CR')
        expect(attachment.source_type).to.eq(AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD)
        expect(attachment.text_content).to.eq('text content')
        expect(attachment.pages).to.eq(11)

    def test_update_attachment_external_created_at_is_none(self):
        attachment = AttachmentFileFactory(
            url='old_url',
            title='old title',
            preview_image_url='http://web.com/image',
            external_last_updated=None,
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='old tag',
            source_type=AttachmentSourceType.PORTAL_COPA,
            text_content='',
            pages=2
        )
        document = create_object({
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 3, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'full_text': 'text content'.encode('utf8'),
            'pages': 10,
            'access': 'public',
        })

        changed = DocumentCloudAttachmentImporter(self.logger).update_attachment(attachment, document)

        expect(changed).to.be.true()
        expect(attachment.url).to.eq('https://www.documentcloud.org/documents/1-CRID-123456-CR.html')
        expect(attachment.title).to.eq('new title')
        expect(attachment.preview_image_url).to.eq('http://web.com/new-image')
        expect(attachment.external_last_updated).to.eq(datetime(2017, 1, 3, tzinfo=pytz.utc))
        expect(attachment.external_created_at).to.eq(datetime(2017, 1, 2, tzinfo=pytz.utc))
        expect(attachment.tag).to.eq('CR')
        expect(attachment.source_type).to.eq(AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD)
        expect(attachment.text_content).to.eq('text content')
        expect(attachment.pages).to.eq(10)

    def test_update_attachment_no_update(self):
        attachment = AttachmentFileFactory(
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            external_last_updated=datetime(2017, 1, 1, tzinfo=pytz.utc)
        )
        document = create_object({
            'updated_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'full_text': 'text content'.encode('utf8'),
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'pages': 7,
            'access': 'public'
        })

        changed = DocumentCloudAttachmentImporter(self.logger).update_attachment(attachment, document)
        expect(changed).to.be.false()

    def test_force_update_attachment(self):
        attachment = AttachmentFileFactory(
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            external_last_updated=datetime(2017, 1, 1, tzinfo=pytz.utc)
        )
        document = create_object({
            'updated_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'full_text': 'text content'.encode('utf8'),
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'pages': 7,
            'access': 'public'
        })

        changed = DocumentCloudAttachmentImporter(
            self.logger, force_update=True
        ).update_attachment(attachment, document)
        expect(changed).to.be.true()

    def test_update_attachment_update_source_type(self):
        attachment = AttachmentFileFactory(
            source_type='',
            external_last_updated=datetime(2017, 1, 1, tzinfo=pytz.utc)
        )
        document = create_object({
            'updated_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'full_text': 'text content'.encode('utf8'),
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'pages': 7,
            'access': 'public',
        })

        changed = DocumentCloudAttachmentImporter(self.logger).update_attachment(attachment, document)
        expect(changed).to.be.true()
        expect(attachment.source_type).to.eq(AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD)

    def test_update_attachment_not_update_full_text_if_manually_updated(self):
        attachment = AttachmentFileFactory(
            source_type='',
            external_last_updated=datetime(2017, 1, 1, tzinfo=pytz.utc),
            text_content='ABC',
            manually_updated=True,
        )
        document = create_object({
            'updated_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'source_type': 'PORTAL_COPA_DOCUMENTCLOUD',
            'full_text': 'text content'.encode('utf8'),
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'pages': 7,
            'access': 'public'
        })

        changed = DocumentCloudAttachmentImporter(self.logger).update_attachment(attachment, document)
        expect(changed).to.be.true()
        expect(attachment.text_content).to.eq('ABC')

    def test_update_attachment_with_access_error(self):
        attachment = AttachmentFileFactory(
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            external_last_updated=datetime(2017, 1, 1, tzinfo=pytz.utc),
            text_content='ABC',
            manually_updated=True,
            pending_documentcloud_id='123456',
            upload_fail_attempts=0,
        )
        document = create_object({
            'documentcloud_id': '123456',
            'updated_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'source_type': 'PORTAL_COPA_DOCUMENTCLOUD',
            'full_text': 'text content'.encode('utf8'),
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'pages': 7,
            'access': 'error',
            'delete': Mock(
                return_value=True
            )
        })

        changed = DocumentCloudAttachmentImporter(self.logger).update_attachment(attachment, document)
        expect(changed).to.be.true()
        expect(attachment.upload_fail_attempts).to.eq(1)
        expect(attachment.pending_documentcloud_id).to.be.none()
        expect(document.delete).to.be.called()

    def test_update_attachment_with_access_public(self):
        attachment = AttachmentFileFactory(
            source_type=AttachmentSourceType.PORTAL_COPA,
            external_last_updated=datetime(2017, 1, 1, tzinfo=pytz.utc),
            text_content='ABC',
            pending_documentcloud_id='123456',
            upload_fail_attempts=0,
        )
        document = create_object({
            'documentcloud_id': '123456',
            'updated_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'source_type': 'PORTAL_COPA_DOCUMENTCLOUD',
            'full_text': 'text content'.encode('utf8'),
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'pages': 7,
            'access': 'public',
        })

        changed = DocumentCloudAttachmentImporter(self.logger).update_attachment(attachment, document)
        expect(changed).to.be.true()
        expect(attachment.source_type).to.eq(AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD)
        expect(attachment.external_id).to.eq('123456')

    def test_update_attachment_with_access_public_and_manually_update(self):
        attachment = AttachmentFileFactory(
            source_type=AttachmentSourceType.PORTAL_COPA,
            external_last_updated=datetime(2017, 1, 1, tzinfo=pytz.utc),
            text_content='ABC',
            manually_updated=True,
            pending_documentcloud_id='123456',
            upload_fail_attempts=0,
        )
        document = create_object({
            'documentcloud_id': '123456',
            'updated_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'source_type': 'PORTAL_COPA_DOCUMENTCLOUD',
            'full_text': 'text content'.encode('utf8'),
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'pages': 7,
            'access': 'public',
            'save': Mock(
                return_value=True
            )
        })

        changed = DocumentCloudAttachmentImporter(self.logger).update_attachment(attachment, document)
        expect(changed).to.be.true()
        expect(attachment.source_type).to.eq(AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD)
        expect(attachment.external_id).to.eq('123456')
        expect(document.save).to.be.called()

    @patch('shared.attachment_importer.aws')
    def test_update_attachments_delete_attachments(self, _):
        AttachmentFileFactory(source_type=AttachmentSourceType.DOCUMENTCLOUD)

        expect(AttachmentFile.objects.count()).to.eq(1)

        DocumentCloudAttachmentImporter(self.logger).update_attachments()

        expect(AttachmentFile.objects.count()).to.eq(0)

    @patch('shared.attachment_importer.aws')
    def test_update_attachments_kept_attachments(self, _):
        kept_attachment = AttachmentFileFactory(source_type=AttachmentSourceType.DOCUMENTCLOUD)
        AttachmentFileFactory(source_type=AttachmentSourceType.DOCUMENTCLOUD)

        expect(AttachmentFile.objects.count()).to.eq(2)

        importer = DocumentCloudAttachmentImporter(self.logger)
        importer.kept_attachments = [kept_attachment]
        importer.update_attachments()

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().id).to.eq(kept_attachment.id)

    @patch('shared.attachment_importer.aws')
    def test_update_attachments_create_new_attachments(self, _):
        allegation = AllegationFactory()
        new_attachment = AttachmentFileFactory.build(
            allegation=allegation,
            title='title',
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD
        )
        expect(AttachmentFile.objects.count()).to.eq(0)

        importer = DocumentCloudAttachmentImporter(self.logger)
        importer.new_attachments = [new_attachment]
        importer.update_attachments()

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().title).to.eq('title')
        expect(AttachmentFile.objects.first().allegation.crid).to.eq(allegation.crid)

    @patch('shared.attachment_importer.aws')
    def test_update_attachments_save_updated_attachments(self, _):
        attachment = AttachmentFileFactory(
            title='old title',
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD
        )
        attachment.title = 'new title'

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().title).to.eq('old title')

        importer = DocumentCloudAttachmentImporter(self.logger)
        importer.updated_attachments = [attachment]
        importer.update_attachments()

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().title).to.eq('new title')

    @patch('document_cloud.importers.DocumentCloudSession')
    def test_reprocess_text(self, MockDocumentCloudSession):
        session = MagicMock()
        session.__enter__ = Mock(return_value=session)
        MockDocumentCloudSession.return_value = session

        importer = DocumentCloudAttachmentImporter(self.logger)
        importer.reprocess_text()

        expect(MockDocumentCloudSession).to.called_with(importer.log_info)
        expect(session.__enter__).to.be.called()
        expect(session.request_reprocess_missing_text_documents).to.be.called()
        expect(session.__exit__).to.be.called()

    @patch(
        'document_cloud.documentcloud_session.DocumentCloudSession.post',
        return_value=Mock(status_code=401, json=Mock(return_value='Unauthorized'))
    )
    def test_reprocess_text_catch_login_failure(self, _):
        DocumentCloudAttachmentImporter(self.logger).reprocess_text()

    @patch(
        'document_cloud.documentcloud_session.DocumentCloudSession.post',
        side_effect=urllib3.exceptions.HTTPError('Invalid request')
    )
    def test_reprocess_text_catch_login_exception(self, _):
        DocumentCloudAttachmentImporter(self.logger).reprocess_text()

    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer-content-test',
        S3_BUCKET_PDF_DIRECTORY='pdf',
        LAMBDA_FUNCTION_UPLOAD_PDF='uploadPdfTest'
    )
    @patch('document_cloud.importers.DocumentCloud')
    @patch('data.models.attachment_file.aws')
    @patch('shared.attachment_importer.aws')
    @patch('document_cloud.importers.send_cr_attachment_available_email')
    @patch('document_cloud.importers.search_all')
    @patch(
        'document_cloud.documentcloud_session.DocumentCloudSession.post',
        side_effect=[
            Mock(status_code=200),
            Mock(status_code=200),
            Mock(status_code=404, json=Mock(return_value='Not Found')),
        ]
    )
    def test_search_and_update_attachments_success(
        self, _, search_all_mock, send_cr_attachment_email_mock, shared_aws_mock, data_aws_mock, document_cloud_mock
    ):
        allegation = AllegationFactory(crid='234')
        new_cloud_document = create_object({
            'documentcloud_id': '999',
            'allegation': allegation,
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/999-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/999-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 3, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8'),
            'pages': 4,
            'access': 'public',
        })
        update_cloud_document_1 = create_object({
            'documentcloud_id': '1',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/1-CRID-234-CR-updated.html',
            'canonical_url': 'https://www.documentcloud.org/documents/1-CRID-234-CR-updated.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-updated',
            'normal_image_url': 'http://web.com/updated-image',
            'updated_at': datetime(2017, 1, 3, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'full_text': 'updated text content'.encode('utf8'),
            'pages': 1,
            'access': 'public',
        })
        update_cloud_document_2 = create_object({
            'documentcloud_id': '3',
            'allegation': allegation,
            'source_type': AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/3-CRID-456-CR-updated.html',
            'canonical_url': 'https://www.documentcloud.org/documents/3-CRID-456-CR-updated.html',
            'document_type': 'CR',
            'title': 'CRID-456-CR-updated',
            'normal_image_url': 'http://summary-reports.com/updated-image',
            'updated_at': datetime(2017, 1, 3, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'full_text': 'summary reports updated text content'.encode('utf8'),
            'pages': 3,
            'access': 'public',
        })
        kept_cloud_document = create_object({
            'documentcloud_id': '2',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8'),
            'pages': 2,
            'access': 'public',
        })
        update_pending_cloud_document = create_object({
            'documentcloud_id': '1111123',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8'),
            'pages': 2,
            'access': 'public',
        })
        kept_pending_cloud_document = create_object({
            'documentcloud_id': '1111124',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8'),
            'pages': 2,
            'access': 'pending',
        })
        error_pending_cloud_document = create_object({
            'documentcloud_id': '1111125',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8'),
            'pages': 2,
            'access': 'error',
            'delete': Mock(return_value=True)
        })
        new_private_cloud_document = create_object({
            'id': '1111126-CRID-234-CR',
            'documentcloud_id': '1111126',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/1111126-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8'),
            'pages': 2,
            'access': 'private',
            'save': Mock()
        })
        new_organization_cloud_document = create_object({
            'id': '1111127-CRID-234-CR',
            'documentcloud_id': '1111127',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/1111127-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8'),
            'pages': 2,
            'access': 'organization',
            'save': Mock()
        })
        updated_private_cloud_document = create_object({
            'id': '1111128-CRID-234-CR',
            'documentcloud_id': '1111128',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/1111128-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/updated-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'updated text content'.encode('utf8'),
            'pages': 2,
            'access': 'private',
            'save': Mock()
        })
        updated_organization_cloud_document = create_object({
            'id': '1111129-CRID-234-CR',
            'documentcloud_id': '1111129',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/1111129-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8'),
            'pages': 2,
            'access': 'organization',
            'save': Mock()
        })
        updated_cloud_document_1 = create_object({
            'id': '1111126-CRID-234-CR',
            'documentcloud_id': '1111126',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/1111126-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8'),
            'pages': 2,
            'access': 'public',
        })
        updated_cloud_document_2 = create_object({
            'id': '1111128-CRID-234-CR',
            'documentcloud_id': '1111128',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'canonical_url': 'https://www.documentcloud.org/documents/1111128-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8'),
            'pages': 2,
            'access': 'public',
        })

        updated_failed = create_object({'access': 'organization'})

        return_values = {
            '1111126-CRID-234-CR': updated_cloud_document_1,
            '1111127-CRID-234-CR': updated_failed,
            '1111128-CRID-234-CR': updated_cloud_document_2,
            '1111129-CRID-234-CR': updated_failed,
        }

        def side_effect(arg):
            return return_values[arg]

        document_cloud_mock().documents.get.side_effect = side_effect

        search_all_mock.return_value = [
            new_cloud_document,
            update_cloud_document_1,
            update_cloud_document_2,
            kept_cloud_document,
            update_pending_cloud_document,
            kept_pending_cloud_document,
            error_pending_cloud_document,
            new_private_cloud_document,
            new_organization_cloud_document,
            updated_private_cloud_document,
            updated_organization_cloud_document,
        ]

        updated_attachment_3 = AttachmentFileFactory(
            external_id='1111128',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            url='https://www.documentcloud.org/documents/2-CRID-234-CR-old.html',
            title='CRID-234-CR-old-title',
            preview_image_url='http://web.com/image-old',
            external_last_updated=datetime(2017, 1, 1, tzinfo=pytz.utc),
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='old tag',
            text_content='old text content'
        )
        AttachmentFileFactory(
            external_id='1111129',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD
        )
        AttachmentFileFactory(
            external_id='111',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA
        )
        AttachmentFileFactory(
            external_id='666',
            allegation=allegation,
            source_type=AttachmentSourceType.DOCUMENTCLOUD
        )
        updated_attachment_1 = AttachmentFileFactory(
            external_id='1',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            url='https://www.documentcloud.org/documents/2-CRID-234-CR-old.html',
            title='CRID-234-CR-old-title',
            preview_image_url='http://web.com/image-old',
            external_last_updated=datetime(2017, 1, 2, tzinfo=pytz.utc),
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='old tag',
            text_content='old text content'
        )
        AttachmentFileFactory(
            external_id='2',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            url='https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            title='CRID-234-CR-2',
            preview_image_url='http://web.com/image',
            external_last_updated=datetime(2017, 1, 2, tzinfo=pytz.utc),
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='CR',
            text_content='text content'
        )
        updated_attachment_2 = AttachmentFileFactory(
            external_id='3',
            allegation=allegation,
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            url='https://www.documentcloud.org/documents/3-CRID-456-CR.html',
            title='CRID-456-CR-3',
            preview_image_url='http://web.com/image',
            external_last_updated=datetime(2017, 1, 2, tzinfo=pytz.utc),
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='CR',
            text_content='text content',
        )
        updated_public_pending_document = AttachmentFileFactory(
            external_id='4-CRID-456-CR.html',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA,
            url='https://www.documentcloud.org/documents/4-CRID-456-CR.html',
            title='CRID-456-CR-3',
            preview_image_url='http://web.com/image',
            external_last_updated=datetime(2017, 1, 2, tzinfo=pytz.utc),
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='CR',
            text_content='text content',
            pending_documentcloud_id='1111123'
        )
        kept_pending_document = AttachmentFileFactory(
            external_id='5-CRID-456-CR',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA,
            url='https://www.documentcloud.org/documents/5-CRID-456-CR.html',
            title='CRID-456-CR-3',
            preview_image_url='http://web.com/image',
            external_last_updated=datetime(2017, 1, 2, tzinfo=pytz.utc),
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='CR',
            text_content='text content',
            pending_documentcloud_id='1111124'
        )
        updated_error_pending_document = AttachmentFileFactory(
            external_id='6-CRID-456-CR',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA,
            url='https://www.documentcloud.org/documents/6-CRID-456-CR.html',
            title='CRID-456-CR-3',
            preview_image_url='http://web.com/image',
            external_last_updated=datetime(2017, 1, 2, tzinfo=pytz.utc),
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='CR',
            text_content='text content',
            pending_documentcloud_id='1111125'
        )

        expect(AttachmentFile.objects.count()).to.eq(10)

        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCloudAttachmentImporter(self.logger).search_and_update_attachments()

        expect(AttachmentFile.objects.count()).to.eq(11)
        expect(AttachmentFile.objects.filter(external_id='666').count()).to.eq(0)
        new_attachment_1 = AttachmentFile.objects.get(external_id='999')
        new_attachment_2 = AttachmentFile.objects.get(external_id='1111126')
        AttachmentFile.objects.get(external_id='2')

        expect(new_private_cloud_document.save).to.be.called_once()
        expect(new_organization_cloud_document.save).to.be.called_once()
        expect(updated_private_cloud_document.save).to.be.called_once()
        expect(updated_organization_cloud_document.save).to.be.called_once()

        for document in [
            updated_attachment_1,
            updated_attachment_2,
            updated_attachment_3,
            updated_public_pending_document,
            updated_error_pending_document
        ]:
            document.refresh_from_db()

        expect(updated_attachment_1.url).to.eq('https://www.documentcloud.org/documents/1-CRID-234-CR-updated.html')
        expect(updated_attachment_1.title).to.eq('CRID-234-CR-updated')
        expect(updated_attachment_1.preview_image_url).to.eq('http://web.com/updated-image')
        expect(updated_attachment_1.external_last_updated).to.eq(datetime(2017, 1, 3, tzinfo=pytz.utc))
        expect(updated_attachment_1.external_created_at).to.eq(datetime(2017, 1, 2, tzinfo=pytz.utc))
        expect(updated_attachment_1.tag).to.eq('CR')
        expect(updated_attachment_1.source_type).to.eq(AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD)
        expect(updated_attachment_1.text_content).to.eq('updated text content')
        expect(updated_attachment_1.pages).to.eq(1)

        expect(updated_attachment_2.url).to.eq('https://www.documentcloud.org/documents/3-CRID-456-CR-updated.html')
        expect(updated_attachment_2.title).to.eq('CRID-456-CR-updated')
        expect(updated_attachment_2.preview_image_url).to.eq('http://summary-reports.com/updated-image')
        expect(updated_attachment_2.external_last_updated).to.eq(datetime(2017, 1, 3, tzinfo=pytz.utc))
        expect(updated_attachment_2.external_created_at).to.eq(datetime(2017, 1, 2, tzinfo=pytz.utc))
        expect(updated_attachment_2.tag).to.eq('CR')
        expect(updated_attachment_2.source_type).to.eq(AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD)
        expect(updated_attachment_2.text_content).to.eq('summary reports updated text content')
        expect(updated_attachment_2.pages).to.eq(3)

        expect(updated_attachment_3.url).to.eq('https://www.documentcloud.org/documents/2-CRID-234-CR.html')
        expect(updated_attachment_3.title).to.eq('CRID-234-CR-2')
        expect(updated_attachment_3.preview_image_url).to.eq('http://web.com/updated-image')
        expect(updated_attachment_3.external_last_updated).to.eq(datetime(2017, 1, 2, tzinfo=pytz.utc))
        expect(updated_attachment_3.external_created_at).to.eq(datetime(2017, 1, 1, tzinfo=pytz.utc))
        expect(updated_attachment_3.tag).to.eq('CR')
        expect(updated_attachment_3.source_type).to.eq(AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD)
        expect(updated_attachment_3.text_content).to.eq('updated text content')
        expect(updated_attachment_3.pages).to.eq(2)

        expect(updated_public_pending_document.source_type).to.eq(AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD)
        expect(updated_public_pending_document.external_id).to.eq('1111123')
        expect(updated_public_pending_document.pending_documentcloud_id).to.be.none()

        expect(kept_pending_document.external_id).to.eq('5-CRID-456-CR')
        expect(kept_pending_document.source_type).to.eq(AttachmentSourceType.PORTAL_COPA)
        expect(kept_pending_document.pending_documentcloud_id).to.eq('1111124')

        expect(updated_error_pending_document.upload_fail_attempts).to.eq(1)
        expect(updated_error_pending_document.pending_documentcloud_id).to.be.none()
        expect(updated_error_pending_document.external_id).to.eq('6-CRID-456-CR')
        expect(error_pending_cloud_document.delete).to.be.called()

        expect(send_cr_attachment_email_mock).to.be.called_once_with([new_attachment_1, new_attachment_2])

        expect(data_aws_mock.lambda_client.invoke_async.call_count).to.eq(7)
        expect(data_aws_mock.lambda_client.invoke_async).to.be.any_call(
            FunctionName='uploadPdfTest',
            InvokeArgs=json.dumps({
                'url': 'https://www.documentcloud.org/documents/999-CRID-234-CR.html',
                'bucket': 'officer-content-test',
                'key': 'pdf/999'
            })
        )
        expect(data_aws_mock.lambda_client.invoke_async).to.be.any_call(
            FunctionName='uploadPdfTest',
            InvokeArgs=json.dumps({
                'url': 'https://www.documentcloud.org/documents/1-CRID-234-CR-updated.html',
                'bucket': 'officer-content-test',
                'key': 'pdf/1'
            })
        )

        crawler_log = DocumentCrawler.objects.order_by('-created_at').first()
        expect(crawler_log.source_type).to.eq(AttachmentSourceType.DOCUMENTCLOUD)
        expect(crawler_log.status).to.eq(DOCUMENT_CRAWLER_SUCCESS)
        expect(crawler_log.num_documents).to.eq(8)
        expect(crawler_log.num_new_documents).to.eq(2)
        expect(crawler_log.num_updated_documents).to.eq(5)
        expect(crawler_log.num_successful_run).to.eq(1)
        expect(crawler_log.log_key).to.eq('documentcloud/documentcloud-2018-04-04-120001.txt')

        log_args = shared_aws_mock.s3.put_object.call_args[1]

        expect(len(log_args)).to.eq(4)
        expect(log_args['Body']).to.contain(
            b'\nUpdated document https://www.documentcloud.org/documents/1111126-CRID-234-CR.html '
            b'access from private to public'
            b'\ncrid 234 https://www.documentcloud.org/documents/1111126-CRID-234-CR.html'
            b'\nCan not update document https://www.documentcloud.org/documents/1111127-CRID-234-CR.html '
            b'access from organization to public'
            b'\nUpdated document https://www.documentcloud.org/documents/1111128-CRID-234-CR.html '
            b'access from private to public'
            b'\nCan not update document https://www.documentcloud.org/documents/1111129-CRID-234-CR.html '
            b'access from organization to public'
        )
        expect(log_args['Body']).to.contain(
            b'\nCreating 2 attachments'
            b'\nUpdating 5 attachments'
            b'\nCurrent Total documentcloud attachments: 8'
            b'\nDone importing!'
        )
        expect(log_args['Body']).to.contain(
            b'================ REQUEST REPROCESS TEXT FOR NO ORC TEXT DOCUMENTS ================'
            b'\n[SUCCESS] Reprocessing text https://www.documentcloud.org/documents/2-CRID-234-CR.html'
            b'\n[FAIL] Reprocessing text https://www.documentcloud.org/documents/999-CRID-234-CR.html '
            b'failed with status code 404: Not Found'
            b'\nSent reprocessing text requests: 1 success, 1 failure, 0 skipped for 2 no-text documents'
        )
        expect(log_args['Bucket']).to.eq('crawler_logs_bucket')
        expect(log_args['Key']).to.eq('documentcloud/documentcloud-2018-04-04-120001.txt')
        expect(log_args['ContentType']).to.eq('text/plain')

    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer-content-test',
        S3_BUCKET_PDF_DIRECTORY='pdf',
        LAMBDA_FUNCTION_UPLOAD_PDF='uploadPdfTest'
    )
    @patch(
        'document_cloud.importers.DocumentCloudAttachmentImporter.search_attachments',
        side_effect=Mock(side_effect=[Exception()])
    )
    @patch('shared.attachment_importer.aws')
    def test_search_and_update_attachments_failure(self, aws_mock, _):
        with freeze_time(datetime(2018, 4, 2, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                source_type=AttachmentSourceType.DOCUMENTCLOUD,
                status=DOCUMENT_CRAWLER_SUCCESS,
                num_documents=5,
                num_new_documents=1,
                num_updated_documents=4,
                num_successful_run=1,
            )
        with freeze_time(datetime(2018, 4, 3, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                source_type=AttachmentSourceType.DOCUMENTCLOUD,
                status=DOCUMENT_CRAWLER_FAILED,
                num_successful_run=1,
            )

        expect(expect(DocumentCrawler.objects.count())).to.eq(2)

        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCloudAttachmentImporter(self.logger).search_and_update_attachments()

        crawler_log = DocumentCrawler.objects.order_by('-created_at').first()
        expect(crawler_log.source_type).to.eq(AttachmentSourceType.DOCUMENTCLOUD)
        expect(crawler_log.status).to.eq(DOCUMENT_CRAWLER_FAILED)
        expect(crawler_log.num_documents).to.eq(0)
        expect(crawler_log.num_new_documents).to.eq(0)
        expect(crawler_log.num_updated_documents).to.eq(0)
        expect(crawler_log.num_successful_run).to.eq(1)
        expect(crawler_log.log_key).to.eq('documentcloud/documentcloud-2018-04-04-120001.txt')

        log_content = b'\nCreating 0 attachments' \
                      b'\nUpdating 0 attachments' \
                      b'\nCurrent Total documentcloud attachments: 0' \
                      b'\nERROR: Error occurred while SEARCH ATTACHMENTS!'

        log_args = aws_mock.s3.put_object.call_args[1]

        expect(len(log_args)).to.eq(4)
        expect(log_args['Body']).to.contain(log_content)
        expect(log_args['Bucket']).to.eq('crawler_logs_bucket')
        expect(log_args['Key']).to.eq('documentcloud/documentcloud-2018-04-04-120001.txt')
        expect(log_args['ContentType']).to.eq('text/plain')

    def test_make_cloud_document_public_with_public_document(self):
        allegation = AllegationFactory(crid='234')
        public_cloud_document = create_object({
            'id': 'CRID-789-CR',
            'documentcloud_id': '777',
            'allegation': allegation,
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
            'access': 'public',
        })

        result = DocumentCloudAttachmentImporter(self.logger).make_cloud_document_public(public_cloud_document)
        expect(result).to.be.true()

    @patch('document_cloud.importers.DocumentCloud')
    def test_make_cloud_document_public_with_private_document(self, document_cloud_mock):
        allegation = AllegationFactory(crid='234')
        save_mock = Mock()
        private_cloud_document = create_object({
            'id': 'CRID-234-CR',
            'documentcloud_id': '777',
            'allegation': allegation,
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/documents/CRID-234-CR.html',
            'access': 'private',
            'save': save_mock
        })
        updated_cloud_document = create_object({
            'id': 'CRID-234-CR',
            'documentcloud_id': '777',
            'allegation': allegation,
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/documents/CRID-234-CR.html',
            'access': 'public',
        })
        document_cloud_mock().documents.get.return_value = updated_cloud_document

        importer = DocumentCloudAttachmentImporter(self.logger)
        importer.log_info = Mock()
        result = importer.make_cloud_document_public(private_cloud_document)

        expect(save_mock).to.be.called_once()
        expect(document_cloud_mock().documents.get).to.be.called_with('CRID-234-CR')
        expect(importer.log_info).to.be.called_with(
            'Updated document https://www.documentcloud.org/documents/CRID-234-CR.html access from private to public'
        )
        expect(result).to.be.true()

    @patch('document_cloud.importers.DocumentCloud')
    def test_make_cloud_document_public_with_organization_document(self, document_cloud_mock):
        allegation = AllegationFactory(crid='234')
        save_mock = Mock()
        private_cloud_document = create_object({
            'id': 'CRID-234-CR',
            'documentcloud_id': '777',
            'allegation': allegation,
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/canonical_url',
            'access': 'organization',
            'save': save_mock
        })
        updated_cloud_document = create_object({
            'id': 'CRID-234-CR',
            'documentcloud_id': '777',
            'allegation': allegation,
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/canonical_url',
            'access': 'public',
        })
        document_cloud_mock().documents.get.return_value = updated_cloud_document

        importer = DocumentCloudAttachmentImporter(self.logger)
        importer.log_info = Mock()
        result = importer.make_cloud_document_public(private_cloud_document)

        expect(save_mock).to.be.called_once()
        expect(document_cloud_mock().documents.get).to.be.called_with('CRID-234-CR')
        expect(importer.log_info).to.be.called_with(
            'Updated document https://www.documentcloud.org/canonical_url access from organization to public'
        )
        expect(result).to.be.true()

    @patch('document_cloud.importers.DocumentCloud')
    def test_make_cloud_document_public_with_private_document_not_updated(self, document_cloud_mock):
        allegation = AllegationFactory(crid='234')
        save_mock = Mock()
        private_cloud_document = create_object({
            'id': 'CRID-234-CR',
            'documentcloud_id': '777',
            'allegation': allegation,
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/canonical_url',
            'access': 'private',
            'save': save_mock
        })

        importer = DocumentCloudAttachmentImporter(self.logger)
        importer.log_info = Mock()
        result = importer.make_cloud_document_public(private_cloud_document)

        expect(document_cloud_mock().documents.get).to.be.called_with('CRID-234-CR')
        expect(importer.log_info).to.be.called_with(
            'Can not update document https://www.documentcloud.org/canonical_url access from private to public'
        )
        expect(result).to.be.false()

    @patch('document_cloud.importers.DocumentCloud')
    def test_make_cloud_document_public_with_organization_document_not_updated(self, document_cloud_mock):
        allegation = AllegationFactory(crid='234')
        save_mock = Mock()
        private_cloud_document = create_object({
            'id': 'CRID-234-CR',
            'documentcloud_id': '777',
            'allegation': allegation,
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/canonical_url',
            'access': 'organization',
            'save': save_mock
        })

        importer = DocumentCloudAttachmentImporter(self.logger)
        importer.log_info = Mock()
        result = importer.make_cloud_document_public(private_cloud_document)

        expect(document_cloud_mock().documents.get).to.be.called_with('CRID-234-CR')
        expect(importer.log_info).to.be.called_with(
            'Can not update document https://www.documentcloud.org/canonical_url access from organization to public'
        )
        expect(result).to.be.false()

    def test_make_cloud_document_public_with_error_document(self):
        allegation = AllegationFactory(crid='234')
        save_mock = Mock()
        error_cloud_document = create_object({
            'id': 'CRID-234-CR',
            'documentcloud_id': '777',
            'allegation': allegation,
            'source_type': AttachmentSourceType.DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/canonical_url',
            'access': 'error',
            'save': save_mock
        })

        importer = DocumentCloudAttachmentImporter(self.logger)
        importer.log_info = Mock()
        result = importer.make_cloud_document_public(error_cloud_document)

        expect(importer.log_info).to.be.called_with(
            'Skip document https://www.documentcloud.org/canonical_url (access: error)'
        )
        expect(result).to.be.false()

    def test_make_cloud_document_public_with_error_document_copa_documentcloud_source_type(self):
        allegation = AllegationFactory(crid='234')
        save_mock = Mock()
        error_cloud_document = create_object({
            'id': 'CRID-234-CR',
            'documentcloud_id': '777',
            'allegation': allegation,
            'source_type': AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            'canonical_url': 'https://www.documentcloud.org/canonical_url',
            'access': 'error',
            'save': save_mock
        })

        result = DocumentCloudAttachmentImporter(self.logger).make_cloud_document_public(error_cloud_document)
        expect(result).to.be.true()
