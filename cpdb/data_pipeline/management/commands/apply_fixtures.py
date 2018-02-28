import re
import os
from tempfile import NamedTemporaryFile

from django.core.management import BaseCommand, call_command, CommandError
from django.conf import settings
from django.core.serializers.base import DeserializationError

from azure.storage.blob import BlockBlobService

from data_pipeline.models import AppliedFixture


class Command(BaseCommand):
    container = 'fixtures'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.block_blob_service = BlockBlobService(
            account_name=settings.DATA_PIPELINE_STORAGE_ACCOUNT_NAME,
            account_key=settings.DATA_PIPELINE_STORAGE_ACCOUNT_KEY
        )

    def get_available_blobs(self):
        blob_names = [blob.name for blob in self.block_blob_service.list_blobs(self.container)]
        pattern = r'^(\d+)_.+'
        return [
            {
                'name': name,
                'id': int(re.findall(pattern, name)[0])
            }
            for name in blob_names
            if re.match(pattern, name) is not None
        ]

    def get_unapplied_blobs(self, blobs):
        applied_blob_ids = AppliedFixture.objects.all().values_list('id', flat=True)
        blobs = [
            blob for blob in blobs
            if blob['id'] not in applied_blob_ids
        ]
        return sorted(blobs, key=lambda blob: blob['id'])

    def try_write_blob(self, blob):
        self.stdout.write('Applying %s ...' % blob['name'])
        tmp_file = NamedTemporaryFile(suffix='.json', dir=os.getcwd(), delete=False)
        try:
            self.block_blob_service.get_blob_to_path(self.container, blob['name'], tmp_file.name)
            call_command('loaddata', tmp_file.name)
            AppliedFixture.objects.create(file_name=blob['name'], id=blob['id'])
        except (CommandError, LookupError, DeserializationError):
            self.stderr.write(
                'Cant load data from fixture %s. '
                'There is something wrong with the fixture file. '
                'Have you migrated schema?' % blob['name']
            )
            return False
        finally:
            os.remove(tmp_file.name)

        return True

    def handle(self, *args, **options):
        available_blobs = self.get_available_blobs()
        unapplied_blobs = self.get_unapplied_blobs(available_blobs)

        for blob in unapplied_blobs:
            if not self.try_write_blob(blob):
                self.stdout.write('Abort.')
                break
        else:
            self.stdout.write('Done.')
