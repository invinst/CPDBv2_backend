from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.test import TestCase

from wagtail.wagtailcore.models import Page

from landing_page.models import LandingPage


class CreatePageIfNotExistTestCase(TestCase):
    def test_create_page(self):
        LandingPage.add_root(
            instance=Page(title='Root', slug='root'))

        management.call_command('create_page_if_not_exist', 'landing_page.LandingPage', 'Landing Page')
        self.assertEqual(LandingPage.objects.first().title, 'Landing Page')

    def test_not_create_page_when_exist(self):
        root = LandingPage.add_root(
            instance=Page(title='Root', slug='root', content_type=ContentType.objects.get_for_model(Page)))

        root.add_child(instance=LandingPage(title='Reporting'))
        self.assertEqual(LandingPage.objects.count(), 1)
