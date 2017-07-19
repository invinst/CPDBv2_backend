from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory, AttachmentFileFactory
)
from data.constants import MEDIA_TYPE_VIDEO, MEDIA_TYPE_AUDIO, MEDIA_TYPE_DOCUMENT


class AllegationTestCase(TestCase):
    def test_address(self):
        allegation = AllegationFactory(add1=3000, add2='Michigan Ave', city='Chicago IL')
        expect(allegation.address).to.eq('3000 Michigan Ave, Chicago IL')

    def test_address_missing_sub_address(self):
        allegation = AllegationFactory(add1=None, add2='', city='')
        expect(allegation.address).to.eq('')
        allegation = AllegationFactory(add1=15, add2='', city='')
        expect(allegation.address).to.eq('15')
        allegation = AllegationFactory(add1=None, add2='abc', city='')
        expect(allegation.address).to.eq('abc')
        allegation = AllegationFactory(add1=None, add2='', city='Chicago')
        expect(allegation.address).to.eq('Chicago')
        allegation = AllegationFactory(add1=15, add2='abc', city='')
        expect(allegation.address).to.eq('15 abc')
        allegation = AllegationFactory(add1=15, add2='', city='Chicago')
        expect(allegation.address).to.eq('15, Chicago')
        allegation = AllegationFactory(add1=None, add2='abc', city='Chicago')
        expect(allegation.address).to.eq('abc, Chicago')

    def test_officer_allegations(self):
        allegation = AllegationFactory()
        OfficerAllegationFactory(id=1, allegation=allegation, officer=OfficerFactory())
        expect(allegation.officer_allegations.count()).to.eq(1)
        expect(allegation.officer_allegations[0].id).to.eq(1)

    def test_complainants(self):
        allegation = AllegationFactory()
        ComplainantFactory(id=1, allegation=allegation)
        expect(allegation.complainants.count()).to.eq(1)
        expect(allegation.complainants[0].id).to.eq(1)

    def test_videos(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(id=1, allegation=allegation, file_type=MEDIA_TYPE_VIDEO)
        expect(allegation.videos.count()).to.eq(1)
        expect(allegation.videos[0].id).to.eq(1)

    def test_audios(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(id=1, allegation=allegation, file_type=MEDIA_TYPE_AUDIO)
        expect(allegation.audios.count()).to.eq(1)
        expect(allegation.audios[0].id).to.eq(1)

    def test_documents(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(id=1, allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        expect(allegation.documents.count()).to.eq(1)
        expect(allegation.documents[0].id).to.eq(1)
