import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.management import call_command

import pytz

from data.models import AttachmentFile
from shared.utils import timing

logger = logging.getLogger('crawler.update_documents')


class Command(BaseCommand):
    help = 'Force update all complaint documents info'

    @timing
    def handle(self, *args, **options):
        logger.info('Forcing update all complaint documents...')
        AttachmentFile.objects.update(external_last_updated=datetime(1969, 1, 1, tzinfo=pytz.utc))
        call_command('update_documents')
