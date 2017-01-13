from django.conf import settings
from django.test.testcases import SimpleTestCase

from robber.expect import expect

from data.models import PoliceUnit


class PoliceUnitTestCase(SimpleTestCase):
    def test_str(self):
        self.assertEqual(str(PoliceUnit(unit_name='lorem')), 'lorem')

    def test_v1_url(self):
        unit = 'unit'
        url = '{domain}/url-mediator/session-builder?unit=unit'.format(domain=settings.V1_URL)
        expect(PoliceUnit(unit_name=unit).v1_url).to.eq(url)
