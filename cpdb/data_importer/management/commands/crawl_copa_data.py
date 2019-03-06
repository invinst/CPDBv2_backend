import logging

from django.core.management import BaseCommand

from data_importer.copa_crawler.importers import CopaPortalAttachmentImporter, CopaSummaryReportsAttachmentImporter
from email_service.service import send_cr_attachment_available_email

logger = logging.getLogger('crawler.crawl_copa_data')


class Command(BaseCommand):
    def handle(self, *args, **options):
        new_attachments = CopaPortalAttachmentImporter(logger).crawl_and_update_attachments()
        new_attachments += CopaSummaryReportsAttachmentImporter(logger).crawl_and_update_attachments()
        send_cr_attachment_available_email(new_attachments)
