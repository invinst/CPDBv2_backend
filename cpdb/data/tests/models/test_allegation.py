from django.test.testcases import TestCase

from robber.expect import expect

from data.constants import MEDIA_TYPE_DOCUMENT
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory,
    AllegationCategoryFactory, AttachmentFileFactory
)


class AllegationTestCase(TestCase):
    def test_address(self):
        allegation = AllegationFactory(add1='3000', add2='Michigan Ave', city='Chicago IL')
        allegation1 = AllegationFactory(add1='', add2='', city='')
        allegation2 = AllegationFactory(add1='', add2=' ', city='')

        expect(allegation.address).to.eq('3000 Michigan Ave, Chicago IL')
        expect(allegation1.address).to.eq('')
        expect(allegation2.address).to.eq('')

    def test_address_missing_sub_address(self):
        allegation = AllegationFactory(add1='', add2='', city='')
        expect(allegation.address).to.eq('')
        allegation = AllegationFactory(add1='15', add2='', city='')
        expect(allegation.address).to.eq('15')
        allegation = AllegationFactory(add1='', add2='abc', city='')
        expect(allegation.address).to.eq('abc')
        allegation = AllegationFactory(add1='', add2='', city='Chicago')
        expect(allegation.address).to.eq('Chicago')
        allegation = AllegationFactory(add1='15', add2='abc', city='')
        expect(allegation.address).to.eq('15 abc')
        allegation = AllegationFactory(add1='15', add2='', city='Chicago')
        expect(allegation.address).to.eq('15, Chicago')
        allegation = AllegationFactory(add1='', add2='abc', city='Chicago')
        expect(allegation.address).to.eq('abc, Chicago')

    def test_address_old_complaint_address(self):
        allegation = AllegationFactory(old_complaint_address='3XX W. 58TH ST.')
        expect(allegation.address).to.eq('3XX W. 58TH ST.')

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

    def test_get_category_names(self):
        allegation = AllegationFactory()

        category1 = AllegationCategoryFactory(category='Use of Force')
        category2 = AllegationCategoryFactory(category='Illegal Search')
        OfficerAllegationFactory(allegation=allegation, allegation_category=category1)
        OfficerAllegationFactory(allegation=allegation, allegation_category=category2)
        expect(allegation.category_names).to.eq(['Illegal Search', 'Use of Force'])

        OfficerAllegationFactory(allegation=allegation, allegation_category=None)
        expect(allegation.category_names).to.eq(['Illegal Search', 'Unknown', 'Use of Force'])

    def test_complainant_races(self):
        allegation = AllegationFactory()
        ComplainantFactory(race='White', allegation=allegation)
        expect(allegation.complainant_races).to.eq(['White'])

        ComplainantFactory(race='White/Hispinic', allegation=allegation)
        expect(allegation.complainant_races).to.eq(['White', 'White/Hispinic'])

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

    def test_documents(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT, show=False)
        attachment1 = AttachmentFileFactory(allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        attachment2 = AttachmentFileFactory(allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        expect(allegation.documents).to.contain(attachment1, attachment2)

    def test_filtered_attachment_files(self):
        allegation = AllegationFactory()
        attachment = AttachmentFileFactory(
            tag='Other', allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        AttachmentFileFactory(
            tag='Other', allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT, show=False)
        AttachmentFileFactory(
            tag='OCIR', allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        AttachmentFileFactory(
            tag='AR', allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT, show=False)
        expect(list(allegation.filtered_attachment_files)).to.eq([attachment])
