from django.test import SimpleTestCase

from robber import expect

from data.utils.interpolate import ScaleThreshold


class ScaleTestCase(SimpleTestCase):
    def test_scale_threshold_with_domain_of_1(self):
        threshold = ScaleThreshold(domain=[1], target_range=['a', 'b'])
        expect(threshold.interpolate(0)).to.eq('a')
        expect(threshold.interpolate(1)).to.eq('b')
        expect(threshold.interpolate(2)).to.eq('b')

    def test_scale_threshold_with_domain_of_2(self):
        threshold = ScaleThreshold(domain=[1, 2], target_range=['a', 'b', 'c'])
        expect(threshold.interpolate(0)).to.eq('a')
        expect(threshold.interpolate(1)).to.eq('b')
        expect(threshold.interpolate(1.5)).to.eq('b')
        expect(threshold.interpolate(2)).to.eq('c')
        expect(threshold.interpolate(3)).to.eq('c')
