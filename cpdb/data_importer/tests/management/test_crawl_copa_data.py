from django.test import TestCase
from django.core.management import call_command

from mock import patch
from robber import expect

from data.factories import AttachmentFileFactory
from data.constants import AttachmentSourceType


class CrawlCopaPortalDataTestCase(TestCase):
    @patch('data_importer.copa_crawler.importers.CopaPortalAttachmentImporter.crawl_and_update_attachments')
    @patch('data_importer.copa_crawler.importers.CopaSummaryReportsAttachmentImporter.crawl_and_update_attachments')
    @patch('data_importer.management.commands.crawl_copa_data.send_cr_attachment_available_email')
    def test_handle(self, send_email_mock, summary_reports_importer_mock, portal_importer_mock):
        attachment_file = AttachmentFileFactory(source_type=AttachmentSourceType.PORTAL_COPA)
        portal_importer_mock.return_value = [attachment_file]

        call_command('crawl_copa_data')
        expect(summary_reports_importer_mock).not_to.be.called()
        expect(send_email_mock).to.be.called_with([attachment_file])
