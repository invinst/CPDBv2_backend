from django.core import management
from django.test import TestCase

from robber import expect

from data.factories import AttachmentFileFactory
from analytics.factories import AttachmentTrackingFactory
from analytics import constants


class UpdateAttachmentDownloadsAndViewsCountTestCase(TestCase):
    def test_update_attachment_downloads_and_views_count(self):
        attachment1 = AttachmentFileFactory(
            id=1,
            views_count=0,
            downloads_count=1
        )
        attachment2 = AttachmentFileFactory(
            id=2,
            views_count=0,
            downloads_count=0
        )
        attachment3 = AttachmentFileFactory(
            id=3,
            views_count=1,
            downloads_count=2
        )

        AttachmentTrackingFactory(
            attachment_file=attachment1,
            kind=constants.VIEW_EVENT_TYPE
        )
        AttachmentTrackingFactory(
            attachment_file=attachment1,
            kind=constants.DOWNLOAD_EVENT_TYPE
        )
        AttachmentTrackingFactory(
            attachment_file=attachment2,
            kind=constants.VIEW_EVENT_TYPE
        )
        AttachmentTrackingFactory(
            attachment_file=attachment2,
            kind=constants.VIEW_EVENT_TYPE
        )

        management.call_command('update_attachment_downloads_and_views_count')

        attachment1.refresh_from_db()
        attachment2.refresh_from_db()
        attachment3.refresh_from_db()

        expect(attachment1.views_count).to.eq(1)
        expect(attachment1.downloads_count).to.eq(1)

        expect(attachment2.views_count).to.eq(2)
        expect(attachment2.downloads_count).to.eq(0)

        expect(attachment3.views_count).to.eq(0)
        expect(attachment3.downloads_count).to.eq(0)
