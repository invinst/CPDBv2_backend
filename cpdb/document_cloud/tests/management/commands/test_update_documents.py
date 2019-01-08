from django.core import management
from django.test import TestCase

from mock import patch
from robber import expect


class UpdateDocumentsCommandTestCase(TestCase):
    @patch('document_cloud.services.update_documents.update_documents')
    def test_attachments_unchanged(self, update_documents_mock):
        management.call_command('update_documents')
        expect(update_documents_mock).to.be.called()
