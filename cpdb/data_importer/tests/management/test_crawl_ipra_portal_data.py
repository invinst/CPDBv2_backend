from datetime import datetime

import pytz
from django.test import TestCase

from mock import patch, PropertyMock
from robber import expect

from data_importer.management.commands.crawl_ipra_portal_data import upload_copa_documents
from data.models import AttachmentFile
from data.factories import AttachmentFileFactory, AllegationFactory
from data.constants import AttachmentSourceType, MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_AUDIO


class UploadServiceTestCase(TestCase):
    @patch('data_importer.management.commands.crawl_ipra_portal_data.DocumentCloud')
    def test_upload_portal_copa_documents(self, DocumentCloudMock):
        DocumentCloudMock().documents.upload.return_value = PropertyMock(
            id='5396984-crid-123-cr-tactical-response-report',
            title='CRID 123 CR Tactical Response Report',
            canonical_url='https://www.documentcloud.org/documents/5396984-tactical-response-report.html',
            normal_image_url='https://www.documentcloud.org/documents/tactical-response-report-p1-normal.gif',
            created_at=datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc),
            updated_at=datetime(2017, 8, 5, 14, 30, 00, tzinfo=pytz.utc),
            resources=None
        )

        allegation = AllegationFactory(crid='123')
        AttachmentFileFactory(
            external_id='123-OCIR-Redacted.pdf',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA,
            file_type=MEDIA_TYPE_DOCUMENT,
            title='Tactical Response Report',
            original_url='https://www.chicagocopa.org/wp-content/uploads/2017/10/Log-1086285-TRR-Redacted.pdf'
        )

        upload_copa_documents()

        copa_documents = AttachmentFile.objects.filter(
            source_type=AttachmentSourceType.PORTAL_COPA,
            file_type=MEDIA_TYPE_DOCUMENT
        )
        expect(copa_documents.count()).to.eq(0)

        AttachmentFile.objects.get(
            external_id='5396984',
            allegation=allegation,
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            file_type=MEDIA_TYPE_DOCUMENT,
            title='CRID 123 CR Tactical Response Report',
            url='https://www.documentcloud.org/documents/5396984-tactical-response-report.html',
            tag='CR',
            external_created_at=datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc),
            external_last_updated=datetime(2017, 8, 5, 14, 30, 00, tzinfo=pytz.utc),
            preview_image_url='https://www.documentcloud.org/documents/tactical-response-report-p1-normal.gif',
        )
        expect(DocumentCloudMock().documents.upload).to.be.called_with(
            'https://www.chicagocopa.org/wp-content/uploads/2017/10/Log-1086285-TRR-Redacted.pdf',
            title='CRID 123 CR Tactical Response Report',
            description=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            access='public',
            force_ocr=True
        )

    @patch('data_importer.management.commands.crawl_ipra_portal_data.DocumentCloud')
    def test_upload_summary_reports_copa_documents(self, DocumentCloudMock):
        DocumentCloudMock().documents.upload.return_value = PropertyMock(
            id='5396984-crid-123-cr-tactical-response-report',
            title='CRID 123 CR Tactical Response Report',
            canonical_url='https://www.documentcloud.org/documents/5396984-tactical-response-report.html',
            normal_image_url='https://www.documentcloud.org/documents/tactical-response-report-p1-normal.gif',
            created_at=datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc),
            updated_at=datetime(2017, 8, 5, 14, 30, 00, tzinfo=pytz.utc),
            resources=None
        )

        allegation = AllegationFactory(crid='123')
        AttachmentFileFactory(
            external_id='123-OCIR-Redacted.pdf',
            allegation=allegation,
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA,
            file_type=MEDIA_TYPE_DOCUMENT,
            title='Tactical Response Report',
            original_url='https://www.chicagocopa.org/wp-content/uploads/2017/10/Log-1086285-TRR-Redacted.pdf'
        )

        upload_copa_documents()

        copa_documents = AttachmentFile.objects.filter(
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA,
            file_type=MEDIA_TYPE_DOCUMENT
        )
        expect(copa_documents.count()).to.eq(0)

        AttachmentFile.objects.get(
            external_id='5396984',
            allegation=allegation,
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            file_type=MEDIA_TYPE_DOCUMENT,
            title='CRID 123 CR Tactical Response Report',
            url='https://www.documentcloud.org/documents/5396984-tactical-response-report.html',
            tag='CR',
            external_created_at=datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc),
            external_last_updated=datetime(2017, 8, 5, 14, 30, 00, tzinfo=pytz.utc),
            preview_image_url='https://www.documentcloud.org/documents/tactical-response-report-p1-normal.gif',
        )
        expect(DocumentCloudMock().documents.upload).to.be.called_with(
            'https://www.chicagocopa.org/wp-content/uploads/2017/10/Log-1086285-TRR-Redacted.pdf',
            title='CRID 123 CR Tactical Response Report',
            description=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            access='public',
            force_ocr=True
        )

    @patch('data_importer.management.commands.crawl_ipra_portal_data.DocumentCloud')
    def test_upload_copa_documents_no_upload(self, DocumentCloudMock):
        AttachmentFileFactory(
            external_id='456-OCIR-2-Redacted.pdf',
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            file_type=MEDIA_TYPE_DOCUMENT
        )
        AttachmentFileFactory(
            external_id='log-1086285-oemc-transmission-1',
            source_type=AttachmentSourceType.PORTAL_COPA,
            file_type=MEDIA_TYPE_AUDIO
        )

        upload_copa_documents()
        expect(DocumentCloudMock().documents.upload).not_to.be.called()
