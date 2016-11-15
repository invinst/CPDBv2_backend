from django.core.management import call_command
from django.test import TestCase

from cms.models import ReportPage


class CMSImportReportingContentCommandTestCase(TestCase):
    def test_call_command(self):
        self.assertEqual(ReportPage.objects.all().count(), 0)
        call_command('cms_import_reporting_content', 'cpdb/cms/tests/files/reporting.csv')
        self.assertEqual(ReportPage.objects.all().count(), 1)
        report_page = ReportPage.objects.first()

        self.assertEqual(report_page.fields['title_value']['blocks'][0]['text'], 'title')
        self.assertEqual(report_page.fields['author_value'], 'author')
        self.assertEqual(report_page.fields['publication_value'], 'publication')
        self.assertEqual(report_page.fields['publish_date_value'], '2015-10-27')
        self.assertEqual(report_page.fields['excerpt_value']['blocks'][0]['text'], 'paragraph 1')
        self.assertEqual(report_page.fields['excerpt_value']['blocks'][1]['text'], 'paragraph 2')
        self.assertEqual(report_page.fields['article_link_value']['blocks'][0]['text'], 'Continue at publication')
        self.assertEqual(report_page.fields['article_link_value']['entityMap']['0']['data']['url'], 'url')
