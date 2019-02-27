from datetime import datetime

from django.test import TestCase
from freezegun import freeze_time

from robber import expect
import pytz
from mock import patch
from django.test import override_settings

from document_cloud.factories import DocumentCrawlerFactory
from document_crawlers.serializers import DocumentCrawlerSerializer


class DocumentCrawlerSerializerTestCase(TestCase):
    @override_settings(S3_BUCKET_CRAWLER_LOG='crawler_logs_bucket')
    @patch('document_cloud.models.document_crawler.aws')
    def test_serialization(self, aws_mock):
        aws_mock.s3.generate_presigned_url.return_value = 'presigned_log_url'

        with freeze_time(lambda: datetime(2018, 10, 20, 12, 0, 1, tzinfo=pytz.utc)):
            document_crawler = DocumentCrawlerFactory(
                id=123,
                source_type='SUMMARY_REPORTS_COPA',
                status='Success',
                num_documents=5,
                num_new_documents=2,
                num_updated_documents=3,
                num_successful_run=6,
                log_key='summary_reports_copa/2019-02-27-100142.txt'
            )

        expect(DocumentCrawlerSerializer(document_crawler).data).to.eq({
            'id': 123,
            'crawler_name': 'SUMMARY_REPORTS_COPA',
            'status': 'Success',
            'num_documents': 5,
            'num_new_documents': 2,
            'recent_run_at': '2018-10-20',
            'num_successful_run': 6,
            'log_url': 'presigned_log_url'
        })
