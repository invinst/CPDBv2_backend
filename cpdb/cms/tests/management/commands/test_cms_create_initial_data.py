from django.core.management import call_command
from django.test import TestCase

from cms.models import SlugPage
from robber import expect


class CSMCreateInitialDataCommandTestCase(TestCase):
    def test_call_command(self):
        call_command('cms_create_initial_data')
        slug_pages = SlugPage.objects.all()
        slug_names = set(page.slug for page in slug_pages)

        expect(slug_pages.count()).to.equal(4)
        expect(slug_names).to.eq({'officer-page', 'landing-page', 'cr-page', 'trr-page'})
