from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from robber import expect
from freezegun import freeze_time

from data.factories import AttachmentFileFactory


class DocumentTestCase(TestCase):
    @freeze_time('2017-01-14 12:00:01')
    def test_list_attachments(self):
        AttachmentFileFactory(
            id=1,
            file_type='document',
            title='CRID 1051117 CR',
            source_type='DOCUMENTCLOUD',
            preview_image_url='http://web.com/image/CRID-1051117-CR-p1-normal.gif',
            views_count=1,
            downloads_count=1
        )
        AttachmentFileFactory(
            id=2,
            file_type='audio',
            title='Log 1087021 911',
            source_type='COPA',
            preview_image_url=None,
            views_count=2,
            downloads_count=2
        )
        AttachmentFileFactory(
            id=3,
            file_type='video',
            title='Log 1086127 Body Worn Camera #1',
            source_type='COPA',
            preview_image_url=None,
            views_count=3,
            downloads_count=3
        )

        expected_data = {
            'count': 3,
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': 1,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'CRID 1051117 CR',
                    'source_type': 'DOCUMENTCLOUD',
                    'preview_image_url': 'http://web.com/image/CRID-1051117-CR-p1-normal.gif',
                    'views_count': 1,
                    'downloads_count': 1
                },
                {
                    'id': 2,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'Log 1087021 911',
                    'source_type': 'COPA',
                    'preview_image_url': None,
                    'views_count': 2,
                    'downloads_count': 2
                },
                {
                    'id': 3,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'Log 1086127 Body Worn Camera #1',
                    'source_type': 'COPA',
                    'preview_image_url': None,
                    'views_count': 3,
                    'downloads_count': 3
                }
            ]
        }

        url = reverse('api-v2:attachment-list', kwargs={})
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)
