from django.test import TestCase

from robber import expect

from analytics.models import AttachmentTracking
from analytics import constants
from data.factories import AttachmentFileFactory


class AttachmentTrackingTestCase(TestCase):
    def test_create_attachment_download_events(self):
        attachments = [
            AttachmentFileFactory(id=1),
            AttachmentFileFactory(id=2)
        ]

        AttachmentTracking.objects.create_attachment_download_events(attachments)

        events = AttachmentTracking.objects.all()

        expect(events).to.have.length(2)
        expect(events[0].attachment_file_id).to.eq(1)
        expect(events[0].kind).to.eq(constants.DOWNLOAD_EVENT_TYPE)
        expect(events[1].attachment_file_id).to.eq(2)
        expect(events[1].kind).to.eq(constants.DOWNLOAD_EVENT_TYPE)
