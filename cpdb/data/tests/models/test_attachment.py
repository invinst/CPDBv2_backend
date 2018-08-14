from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import AttachmentFileFactory
from data.models import AttachmentFile


class DocumentCloudObjectManagerTestCase(TestCase):
    def test_queryset(self):
        AttachmentFileFactory(id=1, file_type='audio')
        AttachmentFileFactory(id=2, file_type='document', url='http://documentcloud.org/1231.html')
        AttachmentFileFactory(id=3, file_type='document', url='http://chicago.org/1231.html')

        documents = AttachmentFile.cloud_document.all()

        expect(documents).to.have.length(1)
        expect(documents[0].id).to.eq(2)
