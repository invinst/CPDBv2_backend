from django.core.management import BaseCommand

from tqdm import tqdm

from data.constants import AttachmentSourceType
from data.models import AttachmentFile


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('external_ids', nargs='*')

    def handle(self, external_ids, *args, **kwargs):
        queryset = AttachmentFile.objects.filter(source_type__in=[
            AttachmentSourceType.DOCUMENTCLOUD, AttachmentSourceType.COPA_DOCUMENTCLOUD
        ])

        if external_ids:
            attachments = queryset.filter(external_id__in=external_ids)
        else:
            attachments = queryset
        for attachment in tqdm(attachments, desc='Send upload pdf requests'):
            attachment.upload_to_s3()
