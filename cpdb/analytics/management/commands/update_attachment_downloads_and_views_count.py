from django.core.management.base import BaseCommand
from django.db.models import OuterRef

from data.models import AttachmentFile
from analytics.models import AttachmentTracking
from analytics import constants
from data.utils.subqueries import SQCount


class Command(BaseCommand):
    help = "Count attachments views and downloads"

    def handle(self, *args, **kwargs):
        AttachmentFile.objects.all().update(views_count=SQCount(
            AttachmentTracking.objects.filter(
                attachment_file_id=OuterRef('id'), kind=constants.VIEW_EVENT_TYPE
            ).values('id')
        ))

        AttachmentFile.objects.all().update(downloads_count=SQCount(
            AttachmentTracking.objects.filter(
                attachment_file_id=OuterRef('id'), kind=constants.DOWNLOAD_EVENT_TYPE
            ).values('id')
        ))
