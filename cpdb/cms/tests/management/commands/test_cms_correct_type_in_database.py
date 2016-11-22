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
        faq.save()

        landing_page_serializer = LandingPageSerializer(data=LandingPageSerializer().fake_data())
        landing_page_serializer.is_valid()
        landing_page_serializer.save()
        landing_page = SlugPage.objects.first()
        landing_page.fields['faq_header_type'] = 'plain_text'
        landing_page.save()

        report_page_serializer = ReportPageSerializer(data=ReportPageSerializer().fake_data())
        report_page_serializer.is_valid()
        report_page_serializer.save()
        report = ReportPage.objects.first()
        report.fields['title_type'] = 'plain_text'
        report.save()

        call_command('cms_correct_type_in_database')
        report.refresh_from_db()
        faq.refresh_from_db()
        landing_page.refresh_from_db()
        self.assertEqual(report.fields['title_type'], 'rich_text')
        self.assertEqual(landing_page.fields['faq_header_type'], 'rich_text')
        self.assertEqual(faq.fields['question_type'], 'rich_text')
