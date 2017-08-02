from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import AllegationFactory, OfficerAllegationFactory, AllegationCategoryFactory


class OfficerAllegationTestCase(TestCase):
    def test_crid(self):
        allegation = AllegationFactory(crid='123456')
        officer_allegation = OfficerAllegationFactory(allegation=allegation)
        expect(officer_allegation.crid).to.eq('123456')

    def test_category(self):
        officer_allegation = OfficerAllegationFactory()
        expect(officer_allegation.category).to.eq(None)

        allegation_category = AllegationCategoryFactory(category='category')
        officer_allegation = OfficerAllegationFactory(allegation_category=allegation_category)
        expect(officer_allegation.category).to.eq('category')

    def test_subcategory(self):
        officer_allegation = OfficerAllegationFactory()
        expect(officer_allegation.subcategory).to.eq(None)

        allegation_category = AllegationCategoryFactory(allegation_name='subcategory')
        officer_allegation = OfficerAllegationFactory(allegation_category=allegation_category)
        expect(officer_allegation.subcategory).to.eq('subcategory')

    def test_coaccused_count(self):
        allegation = AllegationFactory()
        officer_allegation = OfficerAllegationFactory(allegation=allegation)
        OfficerAllegationFactory.create_batch(5, allegation=allegation)

        expect(officer_allegation.coaccused_count).to.eq(6)

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

    def test_final_outcome_display(self):
        officer_allegation = OfficerAllegationFactory(final_outcome='?')
        expect(officer_allegation.final_outcome_display).to.eq('Unknown')

        officer_allegation = OfficerAllegationFactory(final_outcome='100')
        expect(officer_allegation.final_outcome_display).to.eq('Reprimand')

    def test_recc_outcome_display(self):
        officer_allegation = OfficerAllegationFactory(recc_outcome='?')
        expect(officer_allegation.recc_outcome_display).to.eq('Unknown')

        officer_allegation = OfficerAllegationFactory(recc_outcome='100')
        expect(officer_allegation.recc_outcome_display).to.eq('Reprimand')
