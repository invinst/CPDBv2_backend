# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-18 04:42
from __future__ import unicode_literals
from contextlib import contextmanager
from csv import DictReader
import os
from tempfile import NamedTemporaryFile
from operator import itemgetter

from django.conf import settings
from django.db import migrations

from tqdm import tqdm
from azure.storage.blob import BlockBlobService

from shared.utils import timeit
from data.models import OfficerHistory

@contextmanager
def csv_from_azure(filename):
    block_blob_service = BlockBlobService(
        account_name=settings.DATA_PIPELINE_STORAGE_ACCOUNT_NAME,
        account_key=settings.DATA_PIPELINE_STORAGE_ACCOUNT_KEY
    )
    tmp_file = NamedTemporaryFile(suffix='.csv', delete=False)
    block_blob_service.get_blob_to_path('csv', filename, tmp_file.name)
    csvfile = open(tmp_file.name)
    reader = DictReader(csvfile)
    yield reader
    csvfile.close()
    os.remove(tmp_file.name)


def has_change(row, obj):
    return any(str(getattr(obj, k)) != str(row[k]) for k in row)


def bulk_create_update(klass, rows, all_fields=None):
    if not rows:
        return

    all_fields = all_fields or rows[0].keys()

    object_dict = klass.objects.all().only(*all_fields).in_bulk()

    new_objects = [klass(**row) for row in rows if int(row['id']) not in object_dict]
    old_objects = [
        klass(**row) for row in rows
        if row['id'] in object_dict and has_change(row, object_dict[row['id']])]

    timeit(
        lambda: klass.objects.bulk_create(new_objects),
        start_message='Creating {} new objects'.format(len(new_objects))
    )

    if old_objects:
        update_fields = [f for f in all_fields if f != 'id']

        print 'Updating {} old objects'.format(len(old_objects))
        batch_size = 1000
        for i in tqdm(range(0, len(old_objects), batch_size)):
            batch_old_objects = old_objects[i:i + batch_size]
            klass.objects.bulk_update(batch_old_objects, update_fields=update_fields)

    all_ids = map(itemgetter('id'), rows)
    deleted_ids = list(set(object_dict.keys()) - set(all_ids))
    timeit(
        lambda: klass.objects.filter(pk__in=deleted_ids).delete(),
        start_message='Deleting {} objects'.format(len(deleted_ids))
    )


def import_data(apps, schema_editor):
    with csv_from_azure('20181001_officerhistory.csv') as reader:
        blank_or_null = {
            field.name: None if field.null else ''
            for field in OfficerHistory._meta.get_fields()
        }
        all_fields = ['id', 'officer_id', 'unit_id', 'effective_date', 'end_date']

        def clean(row):
            row['id'] = int(row.pop('pk'))
            for key in row.keys():
                if key not in all_fields:
                    row.pop(key)

            for key, val in row.iteritems():
                if val == '':
                    row[key] = blank_or_null[key]

            return row

        rows = map(clean, reader)
        bulk_create_update(OfficerHistory, rows, all_fields)


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0069_import_new_officers_data_20181001'),
    ]

    operations = [
        migrations.RunPython(
            import_data,
            reverse_code=migrations.RunPython.noop,
            elidable=True),
    ]
