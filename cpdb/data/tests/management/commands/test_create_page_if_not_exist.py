from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.test import TestCase

from wagtail.wagtailcore.models import Page

from story.models import ReportingPage


class CreatePageIfNotExistTestCase(TestCase):
    def test_create_page(self):
        ReportingPage.add_root(
            instance=Page(title='Root', slug='root', content_type=ContentType.objects.get_for_model(Page)))

        management.call_command('create_page_if_not_exist', 'story.ReportingPage', 'Reporting')
        self.assertEqual(ReportingPage.objects.first().title, 'Reporting')

    def test_not_create_page_when_exist(self):
        root = ReportingPage.add_root(
            instance=Page(title='Root', slug='root', content_type=ContentType.objects.get_for_model(Page)))

        root.add_child(instance=ReportingPage(title='Reporting'))
        self.assertEqual(ReportingPage.objects.count(), 1)
