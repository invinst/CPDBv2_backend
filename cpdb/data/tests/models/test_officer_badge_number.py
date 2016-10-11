from django.test.testcases import SimpleTestCase

from data.models import OfficerBadgeNumber, Officer


class OfficerBadgeNumberTestCase(SimpleTestCase):
    def test_str(self):
        officer = Officer(first_name='Jeffery', last_name='Aaron')
        self.assertEqual(
            str(OfficerBadgeNumber(officer=officer, star='123456')),
            'Jeffery Aaron - 123456')
