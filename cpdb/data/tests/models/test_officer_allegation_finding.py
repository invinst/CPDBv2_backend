from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import OfficerAllegationFindingFactory


class OfficerAllegationFindingTestCase(TestCase):
    def test_final_finding_display(self):
        officer_allegation = OfficerAllegationFindingFactory(final_finding='?')
        expect(officer_allegation.final_finding_display).to.eq('Unknown')

        officer_allegation = OfficerAllegationFindingFactory(final_finding='UN')
        expect(officer_allegation.final_finding_display).to.eq('Unfounded')

    def test_recc_finding_display(self):
        officer_allegation = OfficerAllegationFindingFactory(recc_finding='?')
        expect(officer_allegation.recc_finding_display).to.eq('Unknown')

        officer_allegation = OfficerAllegationFindingFactory(recc_finding='UN')
        expect(officer_allegation.recc_finding_display).to.eq('Unfounded')
