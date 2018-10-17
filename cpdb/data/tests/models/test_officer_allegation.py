from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import (
    AllegationFactory, OfficerAllegationFactory, AllegationCategoryFactory,
    AttachmentFileFactory, VictimFactory,
)


class OfficerAllegationTestCase(TestCase):
    def test_crid(self):
        allegation = AllegationFactory(crid='123456')
        officer_allegation = OfficerAllegationFactory(allegation=allegation)
        expect(officer_allegation.crid).to.eq('123456')

    def test_category(self):
        officer_allegation = OfficerAllegationFactory(allegation_category=None)
        expect(officer_allegation.category).to.eq(None)

        allegation_category = AllegationCategoryFactory(category='category')
        officer_allegation = OfficerAllegationFactory(allegation_category=allegation_category)
        expect(officer_allegation.category).to.eq('category')

    def test_subcategory(self):
        officer_allegation = OfficerAllegationFactory(allegation_category=None)
        expect(officer_allegation.subcategory).to.eq(None)

        allegation_category = AllegationCategoryFactory(allegation_name='subcategory')
        officer_allegation = OfficerAllegationFactory(allegation_category=allegation_category)
        expect(officer_allegation.subcategory).to.eq('subcategory')

    def test_final_finding_display(self):
        officer_allegation = OfficerAllegationFactory(final_finding='?')
        expect(officer_allegation.final_finding_display).to.eq('Unknown')

        officer_allegation = OfficerAllegationFactory(final_finding='UN')
        expect(officer_allegation.final_finding_display).to.eq('Unfounded')

    def test_recc_finding_display(self):
        officer_allegation = OfficerAllegationFactory(recc_finding='?')
        expect(officer_allegation.recc_finding_display).to.eq('Unknown')

        officer_allegation = OfficerAllegationFactory(recc_finding='UN')
        expect(officer_allegation.recc_finding_display).to.eq('Unfounded')

    def test_attachments(self):
        allegation = AllegationFactory()
        officer_allegation = OfficerAllegationFactory(allegation=allegation)
        attachment_1 = AttachmentFileFactory(allegation=allegation)
        attachment_2 = AttachmentFileFactory(allegation=allegation)

        result = list(officer_allegation.attachments)
        expect(result).to.have.length(2)
        expect(result).to.contain(attachment_1)
        expect(result).to.contain(attachment_2)

    def test_victims(self):
        allegation = AllegationFactory()
        victim1 = VictimFactory(allegation=allegation)
        victim2 = VictimFactory(allegation=allegation)

        officer_allegation = OfficerAllegationFactory(allegation=allegation)
        expect(list(officer_allegation.victims)).to.eq([victim1, victim2])
