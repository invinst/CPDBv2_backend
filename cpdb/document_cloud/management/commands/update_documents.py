import logging

from django.core.management.base import BaseCommand

from document_cloud.importers import DocumentCloudAttachmentImporter

logger = logging.getLogger('crawler.update_documents')


class Command(BaseCommand):
    help = 'Update complaint documents info'

    def handle(self, *args, **options):
        DocumentCloudAttachmentImporter(logger).search_and_update_attachments()
