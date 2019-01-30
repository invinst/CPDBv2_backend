import json
from datetime import datetime

import pytz
from django.test import TestCase, override_settings
from mock import patch
from robber import expect

from data.constants import AttachmentSourceType
from data.factories import AllegationFactory, AttachmentFileFactory
from data.models import AttachmentFile
from document_cloud.models import DocumentCrawler
from document_cloud.services.update_documents import (
    get_attachment, update_documents, update_attachment, save_attachments,
)
from email_service.constants import CR_ATTACHMENT_AVAILABLE
from email_service.factories import EmailTemplateFactory
from shared.tests.utils import create_object


class UpdateDocumentsServiceTestCase(TestCase):
    def test_create_crawler_log(self):
        EmailTemplateFactory(type=CR_ATTACHMENT_AVAILABLE)
        expect(DocumentCrawler.objects.count()).to.eq(0)

        update_documents()

        expect(DocumentCrawler.objects.count()).to.eq(1)

    def test_get_attachment_has_source_type(self):
        allegation = AllegationFactory(crid='123')
        copa_attachment = AttachmentFileFactory(
            allegation=allegation,
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            external_id='1'
        )

        document = create_object({
            'allegation': allegation,
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
            'documentcloud_id': '1',
        })

        expect(get_attachment(document)).to.be.eq(copa_attachment)

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
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'documentcloud_id': '2',
        })

        expect(get_attachment(document)).to.be.eq(copa_attachment)

    def test_get_attachment_return_none(self):
        allegation = AllegationFactory(crid='123')
        AttachmentFileFactory(
            allegation=allegation,
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
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
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'documentcloud_id': '3',
        })

        expect(get_attachment(document)).to.be.eq(None)

    def test_update_attachment_external_created_at_not_none(self):
        attachment = AttachmentFileFactory(
            url='old_url',
            title='old title',
            preview_image_url='http://web.com/image',
            external_last_updated=datetime(2017, 1, 2, tzinfo=pytz.utc),
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='old tag',
            source_type=AttachmentSourceType.COPA,
            text_content=''
        )
        document = create_object({
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 3, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
            'full_text': 'text content'.encode('utf8')
        })

        changed = update_attachment(attachment, document)

        expect(changed).to.be.true()
        expect(attachment.url).to.eq('https://www.documentcloud.org/documents/1-CRID-123456-CR.html')
        expect(attachment.title).to.eq('new title')
        expect(attachment.preview_image_url).to.eq('http://web.com/new-image')
        expect(attachment.external_last_updated).to.eq(datetime(2017, 1, 3, tzinfo=pytz.utc))
        expect(attachment.external_created_at).to.eq(datetime(2017, 1, 2, tzinfo=pytz.utc))
        expect(attachment.tag).to.eq('CR')
        expect(attachment.source_type).to.eq(AttachmentSourceType.COPA_DOCUMENTCLOUD)
        expect(attachment.text_content).to.eq('text content')

    def test_update_attachment_external_created_at_is_none(self):
        attachment = AttachmentFileFactory(
            url='old_url',
            title='old title',
            preview_image_url='http://web.com/image',
            external_last_updated=None,
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='old tag',
            source_type=AttachmentSourceType.COPA,
            text_content=''
        )
        document = create_object({
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 3, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
            'full_text': 'text content'.encode('utf8')
        })

        changed = update_attachment(attachment, document)

        expect(changed).to.be.true()
        expect(attachment.url).to.eq('https://www.documentcloud.org/documents/1-CRID-123456-CR.html')
        expect(attachment.title).to.eq('new title')
        expect(attachment.preview_image_url).to.eq('http://web.com/new-image')
        expect(attachment.external_last_updated).to.eq(datetime(2017, 1, 3, tzinfo=pytz.utc))
        expect(attachment.external_created_at).to.eq(datetime(2017, 1, 2, tzinfo=pytz.utc))
        expect(attachment.tag).to.eq('CR')
        expect(attachment.source_type).to.eq(AttachmentSourceType.COPA_DOCUMENTCLOUD)
        expect(attachment.text_content).to.eq('text content')

    def test_update_attachment_no_update(self):
        attachment = AttachmentFileFactory(
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            external_last_updated=datetime(2017, 1, 1, tzinfo=pytz.utc)
        )
        document = create_object({
            'updated_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
        })

        changed = update_attachment(attachment, document)
        expect(changed).to.be.false()

    def test_update_attachment_update_source_type(self):
        attachment = AttachmentFileFactory(
            source_type='',
            external_last_updated=datetime(2017, 1, 1, tzinfo=pytz.utc)
        )
        document = create_object({
            'updated_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
            'full_text': 'text content'.encode('utf8'),
            'url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'title': 'new title',
            'normal_image_url': 'http://web.com/new-image',
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'document_type': 'CR',
        })

        changed = update_attachment(attachment, document)
        expect(changed).to.be.true()
        expect(attachment.source_type).to.eq(AttachmentSourceType.COPA_DOCUMENTCLOUD)

    def test_save_attachments_delete_attachments(self):
        AttachmentFileFactory(source_type=AttachmentSourceType.DOCUMENTCLOUD)

        expect(AttachmentFile.objects.count()).to.eq(1)

        save_attachments([], [], [])

        expect(AttachmentFile.objects.count()).to.eq(0)

    def test_save_attachments_kept_attachments(self):
        kept_attachment = AttachmentFileFactory(source_type=AttachmentSourceType.DOCUMENTCLOUD)
        AttachmentFileFactory(source_type=AttachmentSourceType.DOCUMENTCLOUD)

        expect(AttachmentFile.objects.count()).to.eq(2)

        save_attachments(kept_attachments=[kept_attachment], new_attachments=[], updated_attachments=[])

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().id).to.eq(kept_attachment.id)

    def test_save_attachments_create_new_attachments(self):
        allegation = AllegationFactory()
        new_attachment = AttachmentFileFactory.build(
            allegation=allegation,
            title='title',
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD
        )
        expect(AttachmentFile.objects.count()).to.eq(0)

        save_attachments(kept_attachments=[], new_attachments=[new_attachment], updated_attachments=[])

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().title).to.eq('title')
        expect(AttachmentFile.objects.first().allegation.crid).to.eq(allegation.crid)

    def test_save_attachments_save_updated_attachments(self):
        attachment = AttachmentFileFactory(title='old title', source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD)
        attachment.title = 'new title'

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().title).to.eq('old title')

        save_attachments(kept_attachments=[], new_attachments=[], updated_attachments=[attachment])

        expect(AttachmentFile.objects.count()).to.eq(1)
        expect(AttachmentFile.objects.first().title).to.eq('new title')

    @patch('document_cloud.services.update_documents.log_changes')
    def test_save_attachments_log_changes(self, log_changes_mock):
        allegation = AllegationFactory()
        new_attachment = AttachmentFileFactory.build(
            title='title',
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            allegation=allegation
        )
        updated_attachment = AttachmentFileFactory(title='old title', source_type=AttachmentSourceType.DOCUMENTCLOUD)
        updated_attachment.title = 'new title'

        save_attachments([], new_attachments=[new_attachment], updated_attachments=[updated_attachment])

        expect(log_changes_mock).to.be.called_with(1, 1)

    @override_settings(S3_BUCKET_OFFICER_CONTENT='officer-content-test', S3_BUCKET_PDF_DIRECTORY='pdf')
    @patch('data.models.attachment_file.aws')
    @patch('document_cloud.services.update_documents.send_cr_attachment_available_email')
    @patch('document_cloud.services.update_documents.search_all')
    def test_update_documents(self, search_all_mock, send_cr_attachment_available_email_mock, aws_mock):
        allegation = AllegationFactory(crid='234')
        new_document = create_object({
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
            'full_text': 'text content'.encode('utf8')
        })
        update_document = create_object({
            'documentcloud_id': '1',
            'allegation': allegation,
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/1-CRID-234-CR-updated.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-updated',
            'normal_image_url': 'http://web.com/updated-image',
            'updated_at': datetime(2017, 1, 3, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'full_text': 'updated text content'.encode('utf8')
        })
        kept_document = create_object({
            'documentcloud_id': '2',
            'allegation': allegation,
            'source_type': AttachmentSourceType.COPA_DOCUMENTCLOUD,
            'url': 'https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            'document_type': 'CR',
            'title': 'CRID-234-CR-2',
            'normal_image_url': 'http://web.com/new-image',
            'updated_at': datetime(2017, 1, 2, tzinfo=pytz.utc),
            'created_at': datetime(2017, 1, 1, tzinfo=pytz.utc),
            'full_text': 'text content'.encode('utf8')
        })
        search_all_mock.return_value = [new_document, update_document, kept_document]

        AttachmentFileFactory(
            external_id='111',
            allegation=allegation,
            source_type=AttachmentSourceType.COPA
        )
        AttachmentFileFactory(
            external_id='666',
            allegation=allegation,
            source_type=AttachmentSourceType.DOCUMENTCLOUD
        )
        AttachmentFileFactory(
            external_id='1',
            allegation=allegation,
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
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
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            url='https://www.documentcloud.org/documents/2-CRID-234-CR.html',
            title='CRID-234-CR-2',
            preview_image_url='http://web.com/image',
            external_last_updated=datetime(2017, 1, 2, tzinfo=pytz.utc),
            external_created_at=datetime(2017, 1, 1, tzinfo=pytz.utc),
            tag='CR',
            text_content='text content'
        )

        expect(AttachmentFile.objects.count()).to.eq(4)

        update_documents()

        expect(AttachmentFile.objects.count()).to.eq(4)
        expect(AttachmentFile.objects.filter(external_id='666').count()).to.eq(0)
        new_attachment = AttachmentFile.objects.get(external_id='999')
        AttachmentFile.objects.get(external_id='2')
        updated_attachment = AttachmentFile.objects.get(external_id='1')

        expect(updated_attachment.url).to.eq('https://www.documentcloud.org/documents/1-CRID-234-CR-updated.html')
        expect(updated_attachment.title).to.eq('CRID-234-CR-updated')
        expect(updated_attachment.preview_image_url).to.eq('http://web.com/updated-image')
        expect(updated_attachment.external_last_updated).to.eq(datetime(2017, 1, 3, tzinfo=pytz.utc))
        expect(updated_attachment.external_created_at).to.eq(datetime(2017, 1, 2, tzinfo=pytz.utc))
        expect(updated_attachment.tag).to.eq('CR')
        expect(updated_attachment.source_type).to.eq(AttachmentSourceType.COPA_DOCUMENTCLOUD)
        expect(updated_attachment.text_content).to.eq('updated text content')

        DocumentCrawler.objects.get(
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            num_documents=3,
            num_new_documents=1,
            num_updated_documents=1
        )

        expect(send_cr_attachment_available_email_mock).to.be.called_once_with([new_attachment])

        expect(aws_mock.lambda_client.invoke_async.call_count).to.eq(2)
        expect(aws_mock.lambda_client.invoke_async).to.be.any_call(
            FunctionName='uploadPdf',
            InvokeArgs=json.dumps({
                'url': 'https://www.documentcloud.org/documents/999-CRID-234-CR.html',
                'bucket': 'officer-content-test',
                'key': 'pdf/999'
            })
        )
        expect(aws_mock.lambda_client.invoke_async).to.be.any_call(
            FunctionName='uploadPdf',
            InvokeArgs=json.dumps({
                'url': 'https://www.documentcloud.org/documents/1-CRID-234-CR-updated.html',
                'bucket': 'officer-content-test',
                'key': 'pdf/1'
            })
        )
