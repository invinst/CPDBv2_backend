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
        ActionResponseFactory(trr=trr, force_type='Physical Force - Stunning', action_sub_category='4')
        ActionResponseFactory(trr=trr, force_type='Taser', action_sub_category='5.1')
        ActionResponseFactory(trr=trr, force_type='Other', action_sub_category=None, person='Subject Action')
        ActionResponseFactory(trr=trr, force_type='Impact Weapon', action_sub_category='5.2')
        ActionResponseFactory(trr=trr, force_type='Taser Display', action_sub_category='3')
        ActionResponseFactory(trr=trr, force_type='Taser Display', action_sub_category='3')

        expect(list(trr.force_types)).to.eq([
            'Impact Weapon',
            'Taser',
            'Physical Force - Stunning',
            'Taser Display'
        ])

    def test_top_force_type(self):
        trr = TRRFactory()
        ActionResponseFactory(trr=trr, force_type='Physical Force - Stunning', action_sub_category='4')
        ActionResponseFactory(trr=trr, force_type='Other', action_sub_category=None, person='Subject Action')
        ActionResponseFactory(trr=trr, force_type='Impact Weapon', action_sub_category='5.2')
        ActionResponseFactory(trr=trr, force_type='Taser Display', action_sub_category='3')

        expect(trr.top_force_type).to.eq('Impact Weapon')

    def test_top_force_type_with_empty_force_type(self):
        trr = TRRFactory()

        expect(trr.top_force_type).to.eq(None)

    def test_v2_to(self):
        trr = TRRFactory()
        expect(trr.v2_to).to.eq(f'/trr/{trr.id}/')

    def test_get_absolute_url(self):
        trr = TRRFactory()
        expect(trr.get_absolute_url()).to.eq(f'/trr/{trr.id}/')
