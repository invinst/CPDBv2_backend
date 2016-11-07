from django.test.testcases import SimpleTestCase

from data.models import Officer


class OfficerTestCase(SimpleTestCase):
    def test_str(self):
        self.assertEqual(str(Officer(first_name='Daniel', last_name='Abate')), 'Daniel Abate')
