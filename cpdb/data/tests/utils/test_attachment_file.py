from django.test import TestCase

from robber import expect

from data.factories import AttachmentFileFactory
from data.models import AttachmentFile
from data.utils.attachment_file import filter_attachments


class PercentileTestCase(TestCase):
    def test_filter_attachments(self):
        AttachmentFileFactory(tag='OCIR')
        AttachmentFileFactory(tag='AR')
        AttachmentFileFactory(tag='CR', title='CRID 1049286 CR Arrest Report Herron')
        AttachmentFileFactory(tag='CR', title='CRID 1049286 CR arrest report Herron')
        AttachmentFileFactory(tag='CR', title='CRID 1049286 CR Arrest Herron')
        AttachmentFileFactory(tag='CR', title='CRID 1049286 CR Herron')

        expect(AttachmentFile.objects.all()).to.have.length(6)

        filtered_attachments = sorted(
            filter_attachments(AttachmentFile.objects.all()),
            key=lambda attachment: attachment.title
        )
        expect(filtered_attachments).to.have.length(2)
        expect(filtered_attachments[0].title).to.eq('CRID 1049286 CR Arrest Herron')
        expect(filtered_attachments[1].title).to.eq('CRID 1049286 CR Herron')
