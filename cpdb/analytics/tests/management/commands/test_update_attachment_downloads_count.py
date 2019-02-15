from django.core import management
from django.test import TestCase

from robber import expect

from data.factories import AttachmentFileFactory
from analytics.models import Event


class UpdateAttachmentDownloadsCountTestCase(TestCase):
    def test_update_attachment_downloads_count(self):
        attachment1 = AttachmentFileFactory(
            id=1,
            downloads_count=0
        )
        attachment2 = AttachmentFileFactory(
            id=2,
            downloads_count=0
        )

        Event.objects.create_attachment_download_events([2])

        management.call_command('update_attachment_downloads_count')

        attachment1.refresh_from_db()
        attachment2.refresh_from_db()

        expect(attachment1.downloads_count).to.eq(0)
        expect(attachment2.downloads_count).to.eq(1)
