import logging

from django.core.management import BaseCommand

from data_importer.copa_crawler.importers import CopaPortalAttachmentImporter
from email_service.service import send_cr_attachment_available_email

logger = logging.getLogger('crawler.crawl_copa_data')


class Command(BaseCommand):
    def handle(self, *args, **options):
        # CopaSummaryReportsAttachmentImporter is no longer run: COPA removed the summary-reports page
        # and now publishes those reports (FSR/Memo PDFs) on each case page, which the portal crawler picks up.
        new_attachments = CopaPortalAttachmentImporter(logger).crawl_and_update_attachments()
        send_cr_attachment_available_email(new_attachments)
