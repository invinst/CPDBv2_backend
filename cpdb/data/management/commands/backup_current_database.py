import os
import subprocess

from django.core.management import BaseCommand
from django.conf import settings

from azure.storage.blob import BlockBlobService
from sh import pwd


# pragma: no cover
class Command(BaseCommand):
    help = 'Dump current database and upload to azure'

    def handle(self, *args, **options):
        os.system('pg_dump cpdb | gzip > cpdb_production_dump_$(date +%Y-%m-%d-%H:%M:%S).sql.gz')
        path = subprocess.check_output(['find', repr(pwd()).strip(), '-name', 'cpdb_production_dump*.sql.gz'])\
            .strip().split('/')[-1]
        block_blob_service = BlockBlobService(
            account_name=settings.AZURE_STORAGE_ACCOUNT_NAME, account_key=settings.AZURE_STORAGE_ACCOUNT_KEY)
        block_blob_service.create_blob_from_path(
            'db-backups', path, path)
        os.system('rm %s' % path)
