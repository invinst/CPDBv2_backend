from django.test import TestCase

from mock import patch, PropertyMock
from robber import expect

from document_cloud.constants import AUTO_UPLOAD_DESCRIPTION
from document_cloud.services import upload_copa_documents
from data.models import AttachmentFile
from data.factories import AttachmentFileFactory, AllegationFactory
from data.constants import AttachmentSourceType, MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_AUDIO


class DocumentcloudServicesTestCase(TestCase):
    @patch('document_cloud.services.DocumentCloud')
    def test_upload_copa_documents(self, DocumentCloudMock):
        DocumentCloudMock().documents.upload.return_value = PropertyMock(
            id='5396984-crid-123-cr-tactical-response-report',
            title='CRID 123 CR Tactical Response Report',
            canonical_url='https://www.documentcloud.org/documents/5396984-tactical-response-report.html',
            normal_image_url='https://www.documentcloud.org/documents/tactical-response-report-p1-normal.gif',
            resources=None
        )

        allegation = AllegationFactory(crid='123')
        AttachmentFileFactory(
            external_id='123-OCIR-Redacted.pdf',
            allegation=allegation,
            source_type=AttachmentSourceType.COPA,
            file_type=MEDIA_TYPE_DOCUMENT,
            title='Tactical Response Report',
            original_url='https://www.chicagocopa.org/wp-content/uploads/2017/10/Log-1086285-TRR-Redacted.pdf'
        )

        upload_copa_documents()

        copa_documents = AttachmentFile.objects.filter(
            source_type=AttachmentSourceType.COPA,
            file_type=MEDIA_TYPE_DOCUMENT
        )
        expect(copa_documents.count()).to.eq(0)

        AttachmentFile.objects.get(
            external_id='5396984',
            allegation=allegation,
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            file_type=MEDIA_TYPE_DOCUMENT,
            title='CRID 123 CR Tactical Response Report',
            url='https://www.documentcloud.org/documents/5396984-tactical-response-report.html',
            tag='CR',
            preview_image_url='https://www.documentcloud.org/documents/tactical-response-report-p1-normal.gif',
        )
        expect(DocumentCloudMock().documents.upload).to.be.called_with(
            'https://www.chicagocopa.org/wp-content/uploads/2017/10/Log-1086285-TRR-Redacted.pdf',
            title='CRID 123 CR Tactical Response Report',
            description=AUTO_UPLOAD_DESCRIPTION,
            access='public',
            force_ocr=True
        )

    @patch('document_cloud.services.DocumentCloud')
    def test_upload_copa_documents_no_upload(self, DocumentCloudMock):
        AttachmentFileFactory(
            external_id='456-OCIR-2-Redacted.pdf',
            source_type=AttachmentSourceType.COPA_DOCUMENTCLOUD,
            file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            external_id='log-1086285-oemc-transmission-1',
            source_type=AttachmentSourceType.COPA,
            file_type=MEDIA_TYPE_AUDIO
        )

        upload_copa_documents()
        expect(DocumentCloudMock().documents.upload).not_to.be.called()
