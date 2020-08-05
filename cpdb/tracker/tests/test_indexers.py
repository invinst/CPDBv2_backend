from django.test import TestCase

from robber import expect

from data.factories import AttachmentFileFactory, AllegationFactory
from tracker.indexers import AttachmentFileIndexer


class AttachmentFileIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(AttachmentFileIndexer().get_queryset().count()).to.eq(0)
        AttachmentFileFactory()
        expect(AttachmentFileIndexer().get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        allegation = AllegationFactory(crid=123456)
        datum = AttachmentFileFactory(
            id=1,
            owner=allegation,
            title='Document Title',
            text_content='This is document text content.',
            show=False,
        )

        expect(
            AttachmentFileIndexer().extract_datum(datum)
        ).to.be.eq({
            'id': 1,
            'crid': 123456,
            'title': 'Document Title',
            'text_content': 'This is document text content.',
            'show': False,
        })
