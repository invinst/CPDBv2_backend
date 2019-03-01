from django.test import override_settings
from django.test.testcases import TestCase
from mock import patch
from robber.expect import expect

from document_cloud.factories import DocumentCrawlerFactory


class DocumentCrawlerTestCase(TestCase):
    @override_settings(S3_BUCKET_CRAWLER_LOG='crawler_logs_bucket')
    @patch('document_cloud.models.document_crawler.aws')
    def test_log_url(self, aws_mock):
        aws_mock.s3.generate_presigned_url.return_value = 'presigned_log_url'

        document_crawler = DocumentCrawlerFactory(
            id=1,
            source_type='SUMMARY_REPORTS_COPA',
            log_key='summary_reports_copa/2019-02-27-100142.txt'
        )

        expect(document_crawler.log_url).to.eq('presigned_log_url')
        expect(aws_mock.s3.generate_presigned_url).to.be.called_with(
            ClientMethod='get_object',
            Params={
                'Bucket': 'crawler_logs_bucket',
                'Key': 'summary_reports_copa/2019-02-27-100142.txt',
            },
            ExpiresIn=604800
        )

    def test_log_url_with_empty_log_key(self):
        document_crawler = DocumentCrawlerFactory(
            id=1,
            source_type='SUMMARY_REPORTS_COPA',
        )

        expect(document_crawler.log_url).to.be.none()
