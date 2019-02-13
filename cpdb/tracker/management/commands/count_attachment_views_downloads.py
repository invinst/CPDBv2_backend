import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from data.models import AttachmentFile
from analytics.models import Event

logger = logging.getLogger('attachment.count_views_and_downloads')


class Command(BaseCommand):
    help = "Count attachments' views and downloads"

    def handle(self, *args, **kwargs):
        logger.info('Attachments views and downloads counting process is about to start...')

        attachments = AttachmentFile.objects.select_for_update().all()
        with transaction.atomic():
            for attachment in attachments:
                views_count = Event.objects.filter(name='attachment-view', data__id=attachment.id).count()
                downloads_count = Event.objects.filter(name='attachment-download', data__id=attachment.id).count()

                attachment.views_count = views_count
                attachment.downloads_count = downloads_count
                attachment.save()
