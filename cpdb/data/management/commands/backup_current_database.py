import os
import subprocess

from django.core.management import BaseCommand
from django.conf import settings

from azure.storage.blob import BlockBlobService
from sh import pwd


# pragma: no cover
class Command(BaseCommand):
    help = 'Dump current database and upload to azure'
    db_config = settings.DATABASES['default']
    database_url = f"postgres://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}" \
        f"/{db_config['NAME']}"

    def add_arguments(self, parser):
        parser.add_argument('--prefix', default='cpdp_production', help='Prefix of dump file')

    def handle(self, *args, **options):
        os.system('pg_dump %s | gzip > %s_dump_$(date +%%Y-%%m-%%d-%%H:%%M:%%S).sql.gz' % (
            self.database_url, options['prefix']
        ))
        path = subprocess.check_output(
            ['find', repr(pwd()).strip(), '-name', '%s_dump*.sql.gz' % options['prefix']]
        ).strip().split('/')[-1]
        block_blob_service = BlockBlobService(
            account_name=settings.AZURE_STORAGE_ACCOUNT_NAME, account_key=settings.AZURE_STORAGE_ACCOUNT_KEY)
        block_blob_service.create_blob_from_path(
            'db-backups', path, path)
        os.system('rm %s' % path)
