from django.core.management import call_command
from django.test import TestCase

from cms.models import SlugPage
from cms.serializers import LandingPageSerializer


class CorrectTypeInDatabaseCommandTestCase(TestCase):
    def test_call_command(self):
        landing_page_serializer = LandingPageSerializer(data=LandingPageSerializer().fake_data())
        landing_page_serializer.is_valid()
        landing_page_serializer.save()
        landing_page = SlugPage.objects.first()
        landing_page.fields['navbar_title_type'] = 'plain_text'
        landing_page.fields.pop('navbar_subtitle_type')
        landing_page.fields.pop('navbar_subtitle_value')
        landing_page.save()

        call_command('cms_correct_type_in_database')
        landing_page.refresh_from_db()
        self.assertEqual(landing_page.fields['navbar_title_type'], 'rich_text')
        self.assertTrue('navbar_subtitle_type' in landing_page.fields)
        self.assertTrue('navbar_subtitle_value' in landing_page.fields)
