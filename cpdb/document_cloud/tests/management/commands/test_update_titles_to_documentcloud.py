from datetime import datetime

from django.core.management import call_command
from django.test import TestCase

from django.utils import timezone
from freezegun import freeze_time
from mock import patch
from robber import expect

from data.constants import AttachmentSourceType
from data.factories import AttachmentFileFactory
from data.models import AttachmentFile


class UpdateDocumentTitlesTestCase(TestCase):

    @patch.object(AttachmentFile, 'update_to_documentcloud')
    def test_update_documents(self, mock_update_to_documentcloud):
        tz = timezone.get_current_timezone()

        with freeze_time(datetime(2016, 10, 7, 12, 0, 1, tzinfo=tz)):
            AttachmentFileFactory(
                title='allegation 1 attachment',
                source_type=AttachmentSourceType.DOCUMENTCLOUD
            )

        with freeze_time(datetime(2016, 10, 6, 0, 0, 0, tzinfo=tz)):
            AttachmentFileFactory(
                title='allegation 2 attachment',
                source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD
            )

        with freeze_time(datetime(2016, 10, 6, 0, 0, 0, tzinfo=tz)):
            AttachmentFileFactory(
                title='allegation 3 attachment',
                source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD
            )

        with freeze_time(datetime(2016, 10, 5, 12, 0, 1, tzinfo=tz)):
            AttachmentFileFactory(
                title='allegation 4 attachment',
                source_type=AttachmentSourceType.DOCUMENTCLOUD
            )

        with freeze_time(datetime(2016, 10, 7, 12, 0, 1, tzinfo=tz)):
            AttachmentFileFactory(
                title='allegation 5 attachment',
                source_type=AttachmentSourceType.PORTAL_COPA
            )

        with freeze_time(datetime(2016, 10, 7, tzinfo=tz)):
            call_command('update_titles_to_documentcloud')

        expect(mock_update_to_documentcloud.call_count).to.eq(3)
        expect(mock_update_to_documentcloud).to.be.any_call('title', 'allegation 1 attachment')
        expect(mock_update_to_documentcloud).to.be.any_call('title', 'allegation 2 attachment')
        expect(mock_update_to_documentcloud).to.be.any_call('title', 'allegation 3 attachment')
