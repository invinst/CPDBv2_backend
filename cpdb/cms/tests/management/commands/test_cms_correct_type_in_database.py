from django.core.management import call_command
from django.test import TestCase

from cms.models import ReportPage, FAQPage, SlugPage
from cms.serializers import ReportPageSerializer, FAQPageSerializer, LandingPageSerializer


class CorrectTypeInDatabaseCommandTestCase(TestCase):
    def test_call_command(self):
        faq_page_serializer = FAQPageSerializer(data=FAQPageSerializer().fake_data())
        faq_page_serializer.is_valid()
        faq_page_serializer.save()
        faq = FAQPage.objects.first()
        faq.fields['question_type'] = 'plain_text'
        faq.fields.pop('answer_type')
        faq.save()

        landing_page_serializer = LandingPageSerializer(data=LandingPageSerializer().fake_data())
        landing_page_serializer.is_valid()
        landing_page_serializer.save()
        landing_page = SlugPage.objects.first()
        landing_page.fields['navbar_title_type'] = 'plain_text'
        landing_page.fields.pop('navbar_subtitle_type')
        landing_page.fields.pop('navbar_subtitle_value')
        landing_page.save()

        report_page_serializer = ReportPageSerializer(data=ReportPageSerializer().fake_data())
        report_page_serializer.is_valid()
        report_page_serializer.save()
        report = ReportPage.objects.first()
        report.fields['title_type'] = 'plain_text'
        report.fields.pop('excerpt_type')
        report.save()

        call_command('cms_correct_type_in_database')
        report.refresh_from_db()
        faq.refresh_from_db()
        landing_page.refresh_from_db()
        self.assertEqual(report.fields['title_type'], 'rich_text')
        self.assertTrue('excerpt_type' in report.fields)
        self.assertEqual(landing_page.fields['navbar_title_type'], 'rich_text')
        self.assertTrue('navbar_subtitle_type' in landing_page.fields)
        self.assertTrue('navbar_subtitle_value' in landing_page.fields)
        self.assertEqual(faq.fields['question_type'], 'rich_text')
        self.assertTrue('answer_type' in faq.fields)
