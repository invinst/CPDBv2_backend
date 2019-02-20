from datetime import datetime

from django.test import TestCase
from freezegun import freeze_time

from robber import expect
import pytz

from document_cloud.factories import DocumentCrawlerFactory
from document_crawlers.serializers import DocumentCrawlerSerializer


class DocumentCrawlerSerializerTestCase(TestCase):
    def test_serialization(self):
        with freeze_time(lambda: datetime(2018, 10, 20, 12, 0, 1, tzinfo=pytz.utc)):
            document_crawler = DocumentCrawlerFactory(
                id=123,
                source_type='SUMMARY_REPORTS_COPA',
                status='Success',
                num_documents=5,
                num_new_documents=2,
                num_updated_documents=3,
                num_successful_run=6
            )

        expect(DocumentCrawlerSerializer(document_crawler).data).to.eq({
            'id': 123,
            'crawler_name': 'SUMMARY_REPORTS_COPA',
            'status': 'Success',
            'num_documents': 5,
            'num_new_documents': 2,
            'recent_run_at': '2018-10-20',
            'num_successful_run': 6
        })
