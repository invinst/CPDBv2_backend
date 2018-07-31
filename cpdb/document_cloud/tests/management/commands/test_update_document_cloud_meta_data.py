from django.test import TestCase

from django.core import management

from mock import MagicMock, patch
from robber import expect

from document_cloud.management.commands.update_document_cloud_meta_data import Command
from data.factories import AttachmentFileFactory


class UpdateDocumentMetaDataCommandTestCase(TestCase):
    def test_get_document_id(self):
        command = Command()
        expect(
            command.get_document_id(AttachmentFileFactory(additional_info={'documentcloud_id': 123}), None)
        ).to.eq(123)
        expect(
            command.get_document_id(AttachmentFileFactory(additional_info=u'{"documentcloud_id": 123}'), None)
        ).to.eq(123)

        document_service = MagicMock()
        document_service.parse_link = MagicMock(return_value={'documentcloud_id': 123})
        expect(
            command.get_document_id(AttachmentFileFactory(additional_info={'documentcloud_id': 123}), document_service)
        ).to.eq(123)

    @patch('document_cloud.management.commands.update_document_cloud_meta_data.DocumentCloud')
    @patch('document_cloud.management.commands.update_document_cloud_meta_data.DocumentcloudService')
    def test_handle(self, DocumentCloudServiceMock, DocumentCloudMock):
        attachment_file = AttachmentFileFactory(
            file_type='document',
            url='http://documentcloud.org/1231.html',
            additional_info={'documentcloud_id': 123}
        )
        document = MagicMock()
        mock_get = DocumentCloudMock().documents.get
        mock_get.return_value = document

        mock_documentcloud_service = DocumentCloudServiceMock()

        management.call_command('update_document_cloud_meta_data')

        mock_documentcloud_service.update_document_meta_data.assert_called_once_with(document, attachment_file)
