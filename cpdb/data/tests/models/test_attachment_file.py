import json
from urllib.error import HTTPError

from django.test import override_settings
from django.test.testcases import TestCase
from documentcloud import DoesNotExistError
from mock import patch, Mock
from robber import expect

from data.factories import AttachmentFileFactory, AllegationFactory
from data.models import AttachmentFile


class AttachmentFileTestCase(TestCase):
    @override_settings(S3_BUCKET_PDF_DIRECTORY='pdf')
    def test_s3_key(self):
        attachment = AttachmentFileFactory(external_id='123')
        expect(attachment.s3_key).to.eq('pdf/123')

    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer-content-test',
        S3_BUCKET_PDF_DIRECTORY='pdf',
        LAMBDA_FUNCTION_UPLOAD_PDF='uploadPdfTest'
    )
    @patch('data.models.attachment_file.aws')
    def test_upload_to_s3(self, mock_aws):
        attachment = AttachmentFileFactory(
            external_id='123',
            url='http://www.chicagocopa.org/wp-content/uploads/2016/05/CHI-R-00000105.pdf'
        )

        attachment.upload_to_s3()

        expect(mock_aws.lambda_client.invoke_async).to.be.any_call(
            FunctionName='uploadPdfTest',
            InvokeArgs=json.dumps({
                'url': 'http://www.chicagocopa.org/wp-content/uploads/2016/05/CHI-R-00000105.pdf',
                'bucket': 'officer-content-test',
                'key': 'pdf/123'
            })
        )

    def test_attachment_shown_manager(self):
        AttachmentFileFactory(id=1)
        AttachmentFileFactory(id=2, show=False)
        AttachmentFileFactory(id=3, show=False)

        shown_attachments = AttachmentFile.showing.all()

        expect(shown_attachments).to.have.length(1)
        expect(shown_attachments[0].id).to.eq(1)

    def test_linked_documents(self):
        allegation = AllegationFactory()
        attachment = AttachmentFileFactory(allegation=allegation, show=True)
        linked_document1 = AttachmentFileFactory(allegation=allegation, file_type='document', show=True)
        linked_document2 = AttachmentFileFactory(allegation=allegation, file_type='document', show=True)
        not_showing_linked_document = AttachmentFileFactory(allegation=allegation, file_type='document', show=False)
        audio = AttachmentFileFactory(allegation=allegation, file_type='audio', show=True)
        video = AttachmentFileFactory(allegation=allegation, file_type='video', show=True)

        expect(attachment.linked_documents).to.contain(linked_document1)
        expect(attachment.linked_documents).to.contain(linked_document2)
        expect(attachment.linked_documents).not_to.contain(not_showing_linked_document)
        expect(attachment.linked_documents).not_to.contain(audio)
        expect(attachment.linked_documents).not_to.contain(video)


class UpdateToDocumentcloudTestCase(TestCase):
    def setUp(self):
        self.document_cloud_patcher = patch('data.models.attachment_file.DocumentCloud')
        self.logger_patcher = patch('data.models.attachment_file.logger')

        self.mock_DocumentCloud = self.document_cloud_patcher.start()
        self.mock_logger = self.logger_patcher.start()

        self.mock_client = Mock()
        self.mock_doc = Mock()
        self.mock_client.documents.get.return_value = self.mock_doc

        self.mock_DocumentCloud.return_value = self.mock_client

    def tearDown(self):
        self.document_cloud_patcher.stop()
        self.logger_patcher.stop()

    def test_not_update_with_wrong_source_type(self):
        attachment = AttachmentFileFactory(source_type='something wrong')
        attachment.update_to_documentcloud('title', 'some title')
        expect(self.mock_client.documents.get).not_to.be.called()
        expect(self.mock_doc.save).not_to.be.called()
        expect(self.mock_logger.error).not_to.be.called()

    def test_not_update_when_cannot_get_documentcloud_document(self):
        self.mock_client.documents.get.side_effect = DoesNotExistError()
        attachment = AttachmentFileFactory(external_id=1, source_type='DOCUMENTCLOUD')
        attachment.update_to_documentcloud('title', 'some title')

        expect(self.mock_doc.save).not_to.be.called()
        expect(self.mock_logger.error).to.be.called_with('Cannot find document with external id 1 on DocumentCloud')

    def test_not_update_when_cannot_save_documentcloud_document(self):
        self.mock_doc.save.side_effect = HTTPError('', '404', '', None, None)
        attachment = AttachmentFileFactory(external_id=1, source_type='DOCUMENTCLOUD')
        attachment.update_to_documentcloud('title', 'some title')

        expect(self.mock_doc.title).to.be.eq('some title')
        expect(self.mock_logger.error).to.be.called_with('Cannot save document with external id 1 on DocumentCloud')

    def test_not_update_when_no_change(self):
        attachment = AttachmentFileFactory(external_id=1, source_type='DOCUMENTCLOUD', title='no changed title')
        setattr(self.mock_doc, 'title', 'no changed title')

        attachment.update_to_documentcloud('title', 'no changed title')

        expect(self.mock_client.documents.get).to.be.called_with(1)
        expect(self.mock_doc.save).not_to.be.called()

    def test_update_successfully(self):
        attachment = AttachmentFileFactory(external_id=1, source_type='DOCUMENTCLOUD')
        attachment.update_to_documentcloud('title', 'some title')

        expect(self.mock_client.documents.get).to.be.called_with(1)
        expect(self.mock_doc.save).to.be.called()
        expect(self.mock_logger.error).not_to.be.called()
        expect(self.mock_doc.title).to.be.eq('some title')
