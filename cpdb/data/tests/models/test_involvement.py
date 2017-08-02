from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import InvolvementFactory


class InvolvementTestCase(TestCase):
    def test_gender_display(self):
        expect(InvolvementFactory(gender='M').gender_display).to.equal('Male')
        expect(InvolvementFactory(gender='F').gender_display).to.equal('Female')
        expect(InvolvementFactory(gender='X').gender_display).to.equal('X')
        expect(InvolvementFactory(gender='?').gender_display).to.equal('?')
