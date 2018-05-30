from django.test.testcases import TestCase
from robber.expect import expect

from trr.factories import TRRFactory, ActionResponseFactory


class OfficerTestCase(TestCase):

    def test_force_category(self):
        expect(TRRFactory(taser=False, firearm_used=False).force_category).to.eq('Other')
        expect(TRRFactory(taser=True, firearm_used=False).force_category).to.eq('Taser')
        expect(TRRFactory(taser=False, firearm_used=True).force_category).to.eq('Firearm')

    def test_actions(self):
        trr = TRRFactory()
        ActionResponseFactory(trr=trr, action='Verbal Commands')
        ActionResponseFactory(trr=trr, action='verbal commands')
        ActionResponseFactory(trr=trr, action='PULLED AWAY')
        ActionResponseFactory(trr=trr, action='Did Not Follow Verbal Direction')

        expect(list(trr.actions)).to.eq([
            'Did Not Follow Verbal Direction',
            'PULLED AWAY',
            'verbal commands',
            'Verbal Commands'
        ])
