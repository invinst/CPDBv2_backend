from django.conf import settings
from django.test.testcases import SimpleTestCase

from robber.expect import expect

from data.models import Officer


class OfficerTestCase(SimpleTestCase):
    def test_str(self):
        self.assertEqual(str(Officer(first_name='Daniel', last_name='Abate')), 'Daniel Abate')

    def test_v1_url(self):
        first = 'first'
        last = 'last'
        url = '{domain}/officer/first-last/1'.format(domain=settings.V1_URL)
        expect(Officer(first_name=first, last_name=last, pk=1).v1_url).to.eq(url)
