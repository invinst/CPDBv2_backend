from django.test import TestCase
from django.core.management import call_command

from mock import patch
from robber import expect

from data.factories import AttachmentFileFactory
from data.constants import AttachmentSourceType


class CrawlIPRAPortalDataTestCase(TestCase):
    @patch('data_importer.ipra_crawler.importers.IpraPortalAttachmentImporter.crawl_and_update_attachments')
    @patch('data_importer.ipra_crawler.importers.IpraSummaryReportsAttachmentImporter.crawl_and_update_attachments')
    @patch('data_importer.management.commands.crawl_ipra_portal_data.send_cr_attachment_available_email')
    def test_handle(self, send_email_mock, summary_reports_importer_mock, portal_importer_mock):
        attachment_file_1 = AttachmentFileFactory(source_type=AttachmentSourceType.PORTAL_COPA)
        attachment_file_2 = AttachmentFileFactory(source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA)
        portal_importer_mock.return_value = [attachment_file_1]
        summary_reports_importer_mock.return_value = [attachment_file_2]

        call_command('crawl_ipra_portal_data')
        expect(send_email_mock).to.be.called_with([attachment_file_1, attachment_file_2])
