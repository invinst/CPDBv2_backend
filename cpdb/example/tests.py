from django.test import TestCase
from django.core.urlresolvers import reverse


class ExampleAPIViewTestCase(TestCase):
    def test_response_code(self):
        response = self.client.get(reverse('super-api'))
        self.assertEqual(response.status_code, 200)
