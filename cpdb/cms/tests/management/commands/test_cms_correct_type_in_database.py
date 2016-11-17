from django.core.management import call_command
from django.test import TestCase

from cms.models import ReportPage
from cms.serializers import ReportPageSerializer


class CorrectTypeInDatabaseCommandTestCase(TestCase):
    def test_call_command(self):
        report_page_serializer = ReportPageSerializer(data=ReportPageSerializer().fake_data())
        report_page_serializer.is_valid()
        report_page_serializer.save()
        report = ReportPage.objects.first()
        report.fields['title_type'] = 'rich_text'
        report.save()
        call_command('cms_correct_type_in_database')
        report = ReportPage.objects.first()
        self.assertEqual(report.fields['title_type'], 'rich_text')
