from django.core.management import call_command
from django.test import TestCase

from cms.models import SlugPage, ReportPage


class SeedCMSDataCommandTestCase(TestCase):
    def test_call_command(self):
        call_command('cms_create_initial_data')
        self.assertEqual(SlugPage.objects.all().count(), 1)
        self.assertEqual(ReportPage.objects.all().count(), 16)
