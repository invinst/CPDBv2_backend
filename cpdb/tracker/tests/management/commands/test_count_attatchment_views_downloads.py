from django.core import management
from django.test import TestCase

from robber import expect

from data.factories import AttachmentFileFactory
from analytics.models import Event


class CountAttachmentViewsDownloadsTestCase(TestCase):
    def test_count_attachment_views_downloads(self):
        attachment1 = AttachmentFileFactory(
            id=1,
            views_count=0,
            downloads_count=0
        )
        attachment2 = AttachmentFileFactory(
            id=2,
            views_count=0,
            downloads_count=0
        )

        Event.objects.create_attachment_download_events([2])
        Event.objects.create_attachment_view_events([1])

        management.call_command('count_attachment_views_downloads')

        attachment1.refresh_from_db()
        attachment2.refresh_from_db()

        expect(attachment1.views_count).to.eq(1)
        expect(attachment1.downloads_count).to.eq(0)

        expect(attachment2.views_count).to.eq(0)
        expect(attachment2.downloads_count).to.eq(1)
