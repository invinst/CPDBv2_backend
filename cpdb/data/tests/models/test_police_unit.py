from django.test.testcases import SimpleTestCase

from data.models import PoliceUnit


class PoliceUnitTestCase(SimpleTestCase):
    def test_str(self):
        self.assertEqual(str(PoliceUnit(unit_name='lorem')), 'lorem')
