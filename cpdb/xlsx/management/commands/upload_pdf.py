import json

from tqdm import tqdm

from django.core.management import BaseCommand
from django.conf import settings

from data.constants import AttachmentSourceType
from data.models import AttachmentFile
from shared.aws import aws


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
            aws.lambda_client.invoke_async(
                FunctionName='uploadPdf',
                InvokeArgs=json.dumps({
                    'url': attachment.url,
                    'bucket': settings.S3_BUCKET_OFFICER_CONTENT,
                    'key': attachment.s3_key
                })
            )
