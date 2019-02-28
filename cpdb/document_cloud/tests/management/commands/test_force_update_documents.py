from datetime import datetime

import pytz
from django.core.management import call_command
from django.test import TestCase
from mock import patch
from robber import expect

from data.constants import AttachmentSourceType
from data.factories import AttachmentFileFactory
from data.models import AttachmentFile


class ForceUpdateDocumentsTestCase(TestCase):
    @patch('document_cloud.management.commands.force_update_documents.call_command')
    def test_handle(self, mock_call_command):
        really_old_datetime = datetime(1969, 1, 1, tzinfo=pytz.utc)
        default_datetime = datetime(2000, 1, 1, tzinfo=pytz.utc)
        AttachmentFileFactory.create_batch(5, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory.create_batch(5, source_type='COPA_DOCUMENTCLOUD')
        AttachmentFileFactory.create_batch(5, external_last_updated=default_datetime, source_type='something wrong')

        call_command('force_update_documents')

        updated_documents = AttachmentFile.objects.filter(
            source_type__in=[AttachmentSourceType.DOCUMENTCLOUD, AttachmentSourceType.COPA_DOCUMENTCLOUD]
        )
        not_updated_documents = AttachmentFile.objects.filter(source_type='something wrong')

        expect(updated_documents.count()).to.eq(10)
        for document in updated_documents:
            expect(document.external_last_updated).to.eq(really_old_datetime)

        expect(not_updated_documents.count()).to.eq(5)
        for document in not_updated_documents:
            expect(document.external_last_updated).to.eq(default_datetime)

        expect(mock_call_command).to.called_with('update_documents')
