from django.core.management import call_command
from django.test import TestCase

from mock import patch, Mock
from robber import expect

from document_cloud.management.commands.update_documents import logger


class UpdateDocumentsTestCase(TestCase):
    @patch('document_cloud.management.commands.update_documents.DocumentCloudAttachmentImporter')
    def test_update_documents(self, MockDocumentCloudAttachmentImporter):
        importer = Mock()
        MockDocumentCloudAttachmentImporter.return_value = importer

        call_command('update_documents')

        expect(MockDocumentCloudAttachmentImporter).to.called_with(
            logger,
            force_update=False
        )

        expect(importer.search_and_update_attachments).to.be.called()

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
