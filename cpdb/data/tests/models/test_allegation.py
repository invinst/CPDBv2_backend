from datetime import date

from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory, AttachmentFileFactory,
    AllegationCategoryFactory, VictimFactory
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

    def test_victims(self):
        allegation = AllegationFactory()
        VictimFactory(id=1, allegation=allegation)
        expect(allegation.victims.count()).to.eq(1)
        expect(allegation.victims[0].id).to.eq(1)

    def test_videos(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(id=1, allegation=allegation, file_type=MEDIA_TYPE_VIDEO)
        expect(allegation.videos.count()).to.eq(0)

    def test_audios(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(id=1, allegation=allegation, file_type=MEDIA_TYPE_AUDIO)
        expect(allegation.audios.count()).to.eq(0)

    def test_documents(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(id=1, allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        expect(allegation.documents.count()).to.eq(1)
        expect(allegation.documents[0].id).to.eq(1)

    def test_exclude_ipra_documents(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(
            id=1, allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT, tag='TRR',
            original_url='original_url_1'
        )
        AttachmentFileFactory(
            id=2, allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT, tag='OBR',
            original_url='original_url_2'
        )
        AttachmentFileFactory(
            id=3, allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT, tag='OCIR',
            original_url='original_url_3'
        )
        AttachmentFileFactory(
            id=4, allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT, tag='AR',
            original_url='original_url_4'
        )
        AttachmentFileFactory(
            id=5, allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT, tag='TAG',
            original_url='original_url_5'
        )
        expect(allegation.documents.count()).to.eq(1)
        expect(allegation.documents[0].id).to.eq(5)

    def test_get_category_names(self):
        allegation = AllegationFactory()

        category1 = AllegationCategoryFactory(category='Use of Force')
        category2 = AllegationCategoryFactory(category='Illegal Search')
        OfficerAllegationFactory(allegation=allegation, allegation_category=category1)
        OfficerAllegationFactory(allegation=allegation, allegation_category=category2)
        expect(allegation.category_names).to.eq(['Illegal Search', 'Use of Force'])

        OfficerAllegationFactory(allegation=allegation)
        expect(allegation.category_names).to.eq(['Illegal Search', 'Unknown', 'Use of Force'])

    def test_complainant_races(self):
        allegation = AllegationFactory()
        ComplainantFactory(race='White', allegation=allegation)
        expect(allegation.complainant_races).to.eq(['White'])

        ComplainantFactory(race='White/Hispinic', allegation=allegation)
        expect(allegation.complainant_races).to.eq(['White/Hispinic', 'White'])

    def test_complainant_age_groups(self):
        allegation = AllegationFactory()
        ComplainantFactory(age=32, allegation=allegation)
        expect(allegation.complainant_age_groups).to.eq(['31-40'])

        ComplainantFactory(age=38, allegation=allegation)
        expect(allegation.complainant_age_groups).to.eq(['31-40'])

        ComplainantFactory(age=55, allegation=allegation)
        expect(allegation.complainant_age_groups).to.eq(['31-40', '51+'])

        allegation_no_complainant = AllegationFactory()
        expect(allegation_no_complainant.complainant_age_groups).to.eq(['Unknown'])

    def test_complainant_genders(self):
        allegation = AllegationFactory()
        ComplainantFactory(gender='F', allegation=allegation)
        expect(allegation.complainant_genders).to.eq(['Female'])

        ComplainantFactory(gender='U', allegation=allegation)
        expect(allegation.complainant_genders).to.eq(['Female', 'Unknown'])

    def test_v2_to_with_officer(self):
        allegation = AllegationFactory(crid='456')
        officer = OfficerFactory(id=123)
        OfficerAllegationFactory(allegation=allegation, officer=officer)

        expect(allegation.v2_to).to.eq('/complaint/456/123/')

    def test_v2_to_without_officer(self):
        allegation = AllegationFactory(crid='456')

        expect(allegation.v2_to).to.eq('/complaint/456/')

    def test_v2_to_with_officerallegation_without_officer(self):
        allegation = AllegationFactory(crid='456')
        OfficerAllegationFactory(allegation=allegation, officer=None)

        expect(allegation.v2_to).to.eq('/complaint/456/')

    def test_first_start_date_and_first_end_date(self):
        allegation1 = AllegationFactory()
        expect(allegation1.first_start_date).to.equal(None)
        expect(allegation1.first_end_date).to.equal(None)

        allegation2 = AllegationFactory()
        OfficerAllegationFactory(allegation=allegation2, start_date=date(2002, 2, 2), end_date=date(2012, 1, 1))
        expect(allegation2.first_start_date).to.eq(date(2002, 2, 2))
        expect(allegation2.first_end_date).to.eq(date(2012, 1, 1))
