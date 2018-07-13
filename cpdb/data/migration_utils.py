"""
WARNING: If you change anything in this file you will affect all migrations
depend on it so think again.
"""

from contextlib import contextmanager
from csv import DictReader
import os
from tempfile import NamedTemporaryFile

from django.conf import settings

from azure.storage.blob import BlockBlobService


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
