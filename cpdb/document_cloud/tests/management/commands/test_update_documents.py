from django.core.management import call_command
from django.test import TestCase

from mock import patch, Mock, MagicMock
from robber import expect

from document_cloud.management.commands.update_documents import logger


class UpdateDocumentsTestCase(TestCase):
    @patch('document_cloud.management.commands.update_documents.DocumentCloudSession')
    @patch('document_cloud.management.commands.update_documents.DocumentCloudAttachmentImporter')
    def test_update_documents(self, MockDocumentCloudAttachmentImporter, MockDocumentCloudSession):
        importer = Mock()
        session = MagicMock()
        session.__enter__ = Mock(return_value=session)

        MockDocumentCloudAttachmentImporter.return_value = importer
        MockDocumentCloudSession.return_value = session

        call_command('update_documents')

        expect(MockDocumentCloudAttachmentImporter).to.called_with(
            logger,
            force_update=False
        )
        expect(importer.search_and_update_attachments).to.be.called()

        expect(MockDocumentCloudSession).to.called_with(logger)
        expect(session.__enter__).to.be.called()
        expect(session.request_reprocess_missing_text_documents_with_delay).to.be.called()
        expect(session.__exit__).to.be.called()

    @patch('document_cloud.management.commands.update_documents.DocumentCloudAttachmentImporter')
    def test_force_update_documents(self, MockDocumentCloudAttachmentImporter):
        importer = Mock()
        MockDocumentCloudAttachmentImporter.return_value = importer

        call_command('update_documents', '--force')

        expect(MockDocumentCloudAttachmentImporter).to.called_with(
            logger,
            force_update=True
        )

        expect(importer.search_and_update_attachments).to.be.called()
