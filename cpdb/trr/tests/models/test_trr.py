from django.test.testcases import TestCase
from robber.expect import expect

from trr.factories import TRRFactory, ActionResponseFactory


class TRRTestCase(TestCase):

    def test_force_category(self):
        expect(TRRFactory(taser=False, firearm_used=False).force_category).to.eq('Other')
        expect(TRRFactory(taser=True, firearm_used=False).force_category).to.eq('Taser')
        expect(TRRFactory(taser=False, firearm_used=True).force_category).to.eq('Firearm')

    def test_force_types(self):
        trr = TRRFactory()
        ActionResponseFactory(trr=trr, force_type='Physical Force - Stunning', action_sub_category=4)
        ActionResponseFactory(trr=trr, force_type='Taser', action_sub_category=5)
        ActionResponseFactory(trr=trr, force_type='Other', action_sub_category=None, person='Subject Action')
        ActionResponseFactory(trr=trr, force_type='Impact Weapon', action_sub_category=5)
        ActionResponseFactory(trr=trr, force_type='Taser Display', action_sub_category=3)
        ActionResponseFactory(trr=trr, force_type='Taser Display', action_sub_category=3)

        expect(list(trr.force_types)).to.eq([
            'Impact Weapon',
            'Taser',
            'Physical Force - Stunning',
            'Taser Display'
        ])
