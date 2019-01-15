import shutil

import boto3
from tqdm import tqdm

from django.core.management import BaseCommand

from data.models import Officer
from django.conf import settings

from xlsx.utils import export_officer_xlsx

s3 = boto3.client('s3')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('officer_ids', nargs='*')

    def handle(self, officer_ids, *args, **kwargs):
        _officer_ids = officer_ids or [officer.id for officer in Officer.objects.all().order_by('id')]

        for officer_id in tqdm(_officer_ids, desc='Uploading officer xlsx'):
            export_officer_xlsx(officer_id, 'tmp')
            file_names = ['accused.xlsx', 'use_of_force.xlsx', 'investigator.xlsx']

            for file_name in file_names:
                s3.upload_file(f'tmp/{file_name}', settings.S3_BUCKET_OFFICER_CONTENT, f'xlsx/{officer_id}/{file_name}')

            shutil.rmtree('tmp', ignore_errors=True)
