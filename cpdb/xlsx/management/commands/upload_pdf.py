import json

import boto3
from tqdm import tqdm

from django.core.management import BaseCommand

from data.models import AttachmentFile


lambda_client = boto3.client('lambda')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('external_ids', nargs='*')

    def handle(self, external_ids, *args, **kwargs):
        queryset = AttachmentFile.objects.filter(source_type__in=['DOCUMENTCLOUD', 'COPA_DOCUMENTCLOUD'])

        if external_ids:
            attachments = queryset.filter(external_id__in=external_ids)
        else:
            attachments = queryset
        for attachment in tqdm(attachments, desc='Send upload pdf requests'):
            lambda_client.invoke_async(
                FunctionName='uploadPdf',
                InvokeArgs=json.dumps({'url': attachment.url, 'key': attachment.external_id})
            )
