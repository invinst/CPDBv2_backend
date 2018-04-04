from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import VictimFactory


class VictimTestCase(TestCase):
    def test_gender_display(self):
        expect(VictimFactory(gender='M').gender_display).to.equal('Male')
        expect(VictimFactory(gender='F').gender_display).to.equal('Female')
        expect(VictimFactory(gender='X').gender_display).to.equal('X')
        expect(VictimFactory(gender='?').gender_display).to.equal('?')
