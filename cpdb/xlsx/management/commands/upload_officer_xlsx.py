from multiprocessing import Pool
import shutil

import boto3
from tqdm import tqdm

from django.core.management import BaseCommand

from data.models import Officer
from django.conf import settings

from xlsx.utils import export_officer_xlsx

s3 = boto3.client('s3')


def upload_xlsx_files(officer):
    tmp_dir = f'tmp/{officer.id}'
    file_names = export_officer_xlsx(officer, tmp_dir)

    for file_name in file_names:
        s3.upload_file(
            f'{tmp_dir}/{file_name}',
            settings.S3_BUCKET_OFFICER_CONTENT,
            f'{settings.S3_BUCKET_XLSX_DIRECTORY}/{officer.id}/{file_name}'
        )

    shutil.rmtree(tmp_dir, ignore_errors=True)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('officer_ids', nargs='*')

    def handle(self, officer_ids, *args, **kwargs):
        if officer_ids:
            officers = Officer.objects.filter(id__in=officer_ids)
        else:
            officers = Officer.objects.all()

        with Pool(20) as p:
            list(tqdm(p.imap(upload_xlsx_files, officers), desc='Uploading officer xlsx', total=officers.count()))
