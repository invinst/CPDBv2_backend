import re
import os
from tempfile import NamedTemporaryFile

from django.core.management import BaseCommand, call_command, CommandError
from django.conf import settings

from azure.storage.blob import BlockBlobService

from data_pipeline.models import AppliedFixture


class Command(BaseCommand):
    def handle(self, *args, **options):
        block_blob_service = BlockBlobService(
            account_name=settings.DATA_PIPELINE_STORAGE_ACCOUNT_NAME,
            account_key=settings.DATA_PIPELINE_STORAGE_ACCOUNT_KEY)
        blob_names = [blob.name for blob in block_blob_service.list_blobs('fixtures')]
        pattern = r'(\d+)_.+'
        blobs = [
            {
                'name': name,
                'id': int(re.findall(pattern, name)[0])
            }
            for name in blob_names
        ]

        applied_blob_ids = AppliedFixture.objects.all().values_list('id', flat=True)
        blobs = [
            blob for blob in blobs
            if blob['id'] not in applied_blob_ids
        ]
        blobs = sorted(blobs, key=lambda blob: blob['id'])

        for blob in blobs:
            self.stdout.write('Applying %s ...' % blob['name'])
            tmp_file = NamedTemporaryFile(suffix='.json', dir=os.getcwd(), delete=False)
            try:
                block_blob_service.get_blob_to_path('fixtures', blob['name'], tmp_file.name)
                call_command('loaddata', tmp_file.name)
            except CommandError:
                self.stderr.write(
                    'Cant load data from fixture %s. '
                    'There is something wrong with the fixture file. '
                    'Have you migrated schema?' % blob['name']
                )
                self.stdout.write('Abort')
                break
            finally:
                os.remove(tmp_file.name)
            AppliedFixture.objects.create(file_name=blob['name'], id=blob['id'])

        self.stdout.write('Done!')
