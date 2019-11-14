import logging

from django.core.management.base import BaseCommand

from document_cloud.importers import DocumentCloudAttachmentImporter

logger = logging.getLogger('crawler.update_documents')


class Command(BaseCommand):
    help = 'Update complaint documents info'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Force update all DocumentCloud documents',
        )

    def handle(self, *args, **options):
        DocumentCloudAttachmentImporter(
            logger,
            force_update=options['force']
        ).search_and_update_attachments()
