from django.core import management
from django.test import TestCase
from mock import patch, MagicMock
from robber import expect

from data.constants import AttachmentSourceType
from data.factories import AttachmentFileFactory


class UpdateDocumentsCommandTestCase(TestCase):
    def test_upload_ipra_documents(self):
        with patch('document_cloud.management.commands.upload_ipra_documents.DocumentCloud') as mock_documentcloud:
            update_doc = AttachmentFileFactory(
                file_type='document',
                source_type=AttachmentSourceType.COPA,
                original_url='http://www.chicagocopa.org/wp-content/uploads/2016/05/CHI-R-00000105.pdf',
                url='http://www.chicagocopa.org/wp-content/uploads/2016/05/CHI-R-00000105.pdf'
            )
            AttachmentFileFactory(file_type='video')
            AttachmentFileFactory(
                file_type='document',
                source_type=AttachmentSourceType.COPA,
                original_url='http://www.chicagocopa.org/wp-content/uploads/2017/05/Arrest-Acuna-REDACTED.pdf',
                url='https://www.documentcloud.org/documents/4195522-CRID-1081170-AR-Acuna.html'
            )
            documentcloud_url = 'https://www.documentcloud.org/documents/4196324-Tactical-Response-Report-Murphy.html'
            mock_upload = mock_documentcloud().documents.upload
            mock_upload.return_value = MagicMock(canonical_url=documentcloud_url)

            management.call_command('upload_ipra_documents')

            mock_upload.assert_called_once_with(
                pdf=update_doc.original_url,
                title=update_doc.title,
                access='organization'
            )

            update_doc.refresh_from_db()
            expect(update_doc.url).to.eq(documentcloud_url)
