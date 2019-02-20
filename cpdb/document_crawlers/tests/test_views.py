from datetime import datetime

import pytz
from django.urls import reverse
from django.test import override_settings
from freezegun import freeze_time

from rest_framework.test import APITestCase
from robber import expect

from document_cloud.factories import DocumentCrawlerFactory


class DocumentCrawlersViewSetTestCase(APITestCase):
    @override_settings(TIME_ZONE='UTC')
    def setUp(self):
        with freeze_time(lambda: datetime(2018, 3, 3, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=1,
                source_type='DOCUMENTCLOUD',
                status='Failed',
                num_documents=5,
                num_new_documents=1,
                num_updated_documents=4,
                num_successful_run=0
            )
        with freeze_time(lambda: datetime(2018, 4, 3, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=2,
                source_type='DOCUMENTCLOUD',
                status='Success',
                num_documents=5,
                num_new_documents=1,
                num_updated_documents=4,
                num_successful_run=1
            )
        with freeze_time(lambda: datetime(2018, 3, 3, 12, 0, 10, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=3,
                source_type='PORTAL_COPA',
                status='Failed',
                num_documents=7,
                num_new_documents=1,
                num_updated_documents=5,
                num_successful_run=0
            )
        with freeze_time(lambda: datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=4,
                source_type='PORTAL_COPA',
                status='Success',
                num_documents=6,
                num_new_documents=2,
                num_updated_documents=4,
                num_successful_run=1
            )
        with freeze_time(lambda: datetime(2018, 3, 3, 12, 0, 20, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=5,
                source_type='SUMMARY_REPORTS_COPA',
                status='Failed',
                num_documents=3,
                num_new_documents=1,
                num_updated_documents=1,
                num_successful_run=0
            )
        with freeze_time(lambda: datetime(2018, 4, 3, 12, 0, 20, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=6,
                source_type='SUMMARY_REPORTS_COPA',
                status='Success',
                num_documents=4,
                num_new_documents=1,
                num_updated_documents=3,
                num_successful_run=1
            )

    def test_list(self):
        url = reverse('api-v2:document-crawlers-list')
        response = self.client.get(url, {'limit': 3})
        expect(response.data['results']).to.eq([
            {
                'id': 6,
                'crawler_name': 'SUMMARY_REPORTS_COPA',
                'status': 'Success',
                'num_documents': 4,
                'num_new_documents': 1,
                'recent_run_at': '2018-04-03',
                'num_successful_run': 1
            },
            {
                'id': 4,
                'crawler_name': 'PORTAL_COPA',
                'status': 'Success',
                'num_documents': 6,
                'num_new_documents': 2,
                'recent_run_at': '2018-04-03',
                'num_successful_run': 1
            },
            {
                'id': 2,
                'crawler_name': 'DOCUMENTCLOUD',
                'status': 'Success',
                'num_documents': 5,
                'num_new_documents': 1,
                'recent_run_at': '2018-04-03',
                'num_successful_run': 1
            }
        ])

    def test_pagination_list(self):
        url = reverse('api-v2:document-crawlers-list')
        response = self.client.get(url, {'limit': 3, 'offset': 3})
        expect(response.data['results']).to.eq([
            {
                'id': 5,
                'crawler_name': 'SUMMARY_REPORTS_COPA',
                'status': 'Failed',
                'num_documents': 3,
                'num_new_documents': 1,
                'recent_run_at': '2018-03-03',
                'num_successful_run': 0
            },
            {
                'id': 3,
                'crawler_name': 'PORTAL_COPA',
                'status': 'Failed',
                'num_documents': 7,
                'num_new_documents': 1,
                'recent_run_at': '2018-03-03',
                'num_successful_run': 0
            },
            {
                'id': 1,
                'crawler_name': 'DOCUMENTCLOUD',
                'status': 'Failed',
                'num_documents': 5,
                'num_new_documents': 1,
                'recent_run_at': '2018-03-03',
                'num_successful_run': 0
            }
        ])
