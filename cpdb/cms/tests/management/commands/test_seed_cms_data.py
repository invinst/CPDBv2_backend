from django.core.management import call_command
from django.test import TestCase

from cms.models import SlugPage


class SeedCMSDataCommandTestCase(TestCase):
    def test_call_command(self):
        call_command('cms_create_initial_data')
        self.assertEqual(SlugPage.objects.all().count(), 1)
