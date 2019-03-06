import logging

from django.core.management import BaseCommand

from data_importer.ipra_crawler.importers import IpraPortalAttachmentImporter, IpraSummaryReportsAttachmentImporter
from email_service.service import send_cr_attachment_available_email

logger = logging.getLogger('crawler.crawl_ipra_portal_data')


class Command(BaseCommand):
    def handle(self, *args, **options):
        new_attachments = IpraPortalAttachmentImporter(logger).crawl_and_update_attachments()
        new_attachments += IpraSummaryReportsAttachmentImporter(logger).crawl_and_update_attachments()
        send_cr_attachment_available_email(new_attachments)
