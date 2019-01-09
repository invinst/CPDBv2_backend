import logging

from django.core.management.base import BaseCommand

from document_cloud.services.update_documents import update_documents

logger = logging.getLogger('django.command')


class Command(BaseCommand):
    help = 'Update complaint documents info'

    def handle(self, *args, **options):
        logger.info('Documentcloud crawling process is about to start...')
        update_documents()
