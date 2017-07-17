from django.test.testcases import SimpleTestCase

from robber.expect import expect

from data.models import Officer, OfficerBadgeNumber


class OfficerBadgeNumberTestCase(SimpleTestCase):
    def test_str(self):
        officer = Officer(first_name='Jeffery', last_name='Aaron')
        expect(
            str(OfficerBadgeNumber(officer=officer, star='123456'))
        ).to.eq('Jeffery Aaron - 123456')
