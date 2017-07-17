from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import ComplainantFactory


class ComplainantTestCase(TestCase):
    def test_gender_display(self):
        expect(ComplainantFactory(gender='M').gender_display).to.equal('Male')
        expect(ComplainantFactory(gender='F').gender_display).to.equal('Female')
        expect(ComplainantFactory(gender='X').gender_display).to.equal('X')
        expect(ComplainantFactory(gender='?').gender_display).to.equal('?')
