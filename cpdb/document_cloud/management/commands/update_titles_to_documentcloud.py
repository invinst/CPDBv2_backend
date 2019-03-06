from datetime import timedelta, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from data.constants import AttachmentSourceType
from data.models import AttachmentFile
from shared.utils import timing


class Command(BaseCommand):
    help = 'Update document titles to Document Cloud'

    @timing
    def handle(self, *args, **options):
        today = timezone.now().date()
        beginning_of_today = datetime(
            today.year, today.month, today.day,
            tzinfo=timezone.get_current_timezone()
        )
        beginning_of_yesterday = beginning_of_today - timedelta(days=1)
        attachments = AttachmentFile.objects.filter(
            updated_at__gte=beginning_of_yesterday,
            source_type__in=AttachmentSourceType.DOCUMENTCLOUD_SOURCE_TYPES
        )

        for attachment in attachments:
            attachment.update_to_documentcloud('title', attachment.title)
