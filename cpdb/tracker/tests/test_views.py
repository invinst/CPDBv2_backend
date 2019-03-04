import time
from datetime import datetime
from operator import itemgetter

import pytz
from django.test import override_settings
from django.urls import reverse
from mock import patch
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from robber import expect
from freezegun import freeze_time
from urllib.parse import urlencode

from authentication.factories import AdminUserFactory
from data.factories import AttachmentFileFactory, AllegationFactory, UserFactory
from data.models import AttachmentFile
from document_cloud.factories import DocumentCrawlerFactory


class AttachmentAPITestCase(APITestCase):
    def test_retrieve_unauthenticated_user(self):
        user = UserFactory(username='test user')
        allegation = AllegationFactory(crid='456')
        attachment = AttachmentFileFactory(
            id=123,
            allegation=allegation,
            title='CR document',
            text_content='CHICAGO POLICE DEPARTMENT RD I HT334604',
            url='http://foo.com',
            preview_image_url='https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            source_type='DOCUMENTCLOUD',
            show=True,
            file_type='document',
            pages=10,
            last_updated_by=user,
            views_count=100
        )
        attachment.created_at = datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc)
        with freeze_time('2017-08-05 12:00:01'):
            attachment.save()

        AttachmentFileFactory(
            id=124,
            allegation=allegation,
            show=True,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/124/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )
        AttachmentFileFactory(
            id=125,
            allegation=allegation,
            show=True,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )
        AttachmentFileFactory(
            id=126,
            allegation=allegation,
            show=False,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )
        AttachmentFileFactory(
            id=127,
            allegation=allegation,
            show=True,
            file_type='audio',
            preview_image_url='',
            original_url='http://audio_link',
        )

        response = self.client.get(reverse('api-v2:attachments-detail', kwargs={'pk': '123'}))
        response.data['linked_documents'] = sorted(response.data['linked_documents'], key=itemgetter('id'))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 123,
            'crid': '456',
            'title': 'CR document',
            'text_content': 'CHICAGO POLICE DEPARTMENT RD I HT334604',
            'url': 'http://foo.com',
            'preview_image_url': 'https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            'original_url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'created_at': '2017-08-04T09:30:00-05:00',
            'updated_at': '2017-08-05T07:00:01-05:00',
            'crawler_name': 'Document Cloud',
            'linked_documents': [
                {
                    'id': 124,
                    'preview_image_url': 'https://assets.documentcloud.org/124/CRID-456-CR-p1-normal.gif',
                },
                {
                    'id': 125,
                    'preview_image_url': 'https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
                }
            ],
            'pages': 10,
            'last_updated_by': 'test user'
        })

        expect(
            self.client.get(reverse('api-v2:attachments-detail', kwargs={'pk': '126'})).status_code
        ).to.be.eq(status.HTTP_404_NOT_FOUND)

    def test_retrieve_authenticated_user(self):
        user = UserFactory(username='test user')

        allegation = AllegationFactory(crid='456')
        attachment = AttachmentFileFactory(
            id=123,
            allegation=allegation,
            title='CR document',
            text_content='CHICAGO POLICE DEPARTMENT RD I HT334604',
            url='http://foo.com',
            preview_image_url='https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            source_type='DOCUMENTCLOUD',
            show=True,
            file_type='document',
            pages=10,
            last_updated_by=user,
            views_count=100,
            downloads_count=99,
            notifications_count=200,
        )
        attachment.created_at = datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc)
        with freeze_time('2017-08-05 12:00:01'):
            attachment.save()

        AttachmentFileFactory(
            id=124,
            allegation=allegation,
            show=True,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/124/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )
        AttachmentFileFactory(
            id=125,
            allegation=allegation,
            show=True,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )
        AttachmentFileFactory(
            id=126,
            allegation=allegation,
            show=False,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )
        AttachmentFileFactory(
            id=127,
            allegation=allegation,
            show=True,
            file_type='audio',
            preview_image_url='',
            original_url='http://audio_link',
        )

        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(reverse('api-v2:attachments-detail', kwargs={'pk': '123'}))
        response.data['linked_documents'] = sorted(response.data['linked_documents'], key=itemgetter('id'))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 123,
            'crid': '456',
            'title': 'CR document',
            'text_content': 'CHICAGO POLICE DEPARTMENT RD I HT334604',
            'url': 'http://foo.com',
            'preview_image_url': 'https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            'original_url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'created_at': '2017-08-04T09:30:00-05:00',
            'updated_at': '2017-08-05T07:00:01-05:00',
            'crawler_name': 'Document Cloud',
            'linked_documents': [
                {
                    'id': 124,
                    'preview_image_url': 'https://assets.documentcloud.org/124/CRID-456-CR-p1-normal.gif',
                },
                {
                    'id': 125,
                    'preview_image_url': 'https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
                }
            ],
            'pages': 10,
            'last_updated_by': 'test user',
            'views_count': 100,
            'downloads_count': 99,
            'notifications_count': 200,
        })

        expect(
            self.client.get(reverse('api-v2:attachments-detail', kwargs={'pk': '126'})).status_code
        ).to.be.eq(status.HTTP_200_OK)

    @freeze_time('2017-01-14 12:00:01')
    def test_list_attachments(self):
        allegation1 = AllegationFactory(crid=123)
        allegation2 = AllegationFactory(crid=456)
        AttachmentFileFactory(
            allegation=allegation1,
            id=1,
            file_type='document',
            title='CRID 1051117 CR',
            source_type='DOCUMENTCLOUD',
            preview_image_url='http://web.com/image/CRID-1051117-CR-p1-normal.gif',
            views_count=1,
            downloads_count=1,
        )
        AttachmentFileFactory(
            allegation=allegation1,
            id=2,
            file_type='audio',
            title='Log 1087021 911',
            source_type='COPA',
            preview_image_url=None,
            views_count=2,
            downloads_count=2,
        )
        AttachmentFileFactory(
            allegation=allegation2,
            id=3,
            file_type='video',
            title='Log 1086127 Body Worn Camera #1',
            source_type='COPA',
            preview_image_url=None,
            views_count=3,
            downloads_count=3,
        )
        AttachmentFileFactory(id=4, allegation=allegation2, show=False)

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
                    'downloads_count': 1,
                    'crid': '123',
                    'show': True,
                    'documents_count': 2,
                },
                {
                    'id': 2,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'Log 1087021 911',
                    'source_type': 'COPA',
                    'preview_image_url': None,
                    'views_count': 2,
                    'downloads_count': 2,
                    'crid': '123',
                    'show': True,
                    'documents_count': 2,
                },
                {
                    'id': 3,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'Log 1086127 Body Worn Camera #1',
                    'source_type': 'COPA',
                    'preview_image_url': None,
                    'views_count': 3,
                    'downloads_count': 3,
                    'crid': '456',
                    'show': True,
                    'documents_count': 1,
                }
            ]
        }

        url = reverse('api-v2:attachments-list', kwargs={})
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)

    def test_update_attachment_visibility(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        AttachmentFileFactory(id=1)

        url = reverse('api-v2:attachments-detail', kwargs={'pk': '1'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'show': False}, format='json')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(AttachmentFile.objects.get(pk=1).show).to.be.false()

    def test_update_attachment_bad_request(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        AttachmentFileFactory(id=1)

        url = reverse('api-v2:attachments-detail', kwargs={'pk': '1'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {}, format='json')

        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

    def test_update_attachment_with_invalid_pk(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        AttachmentFileFactory(id=1)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('api-v2:attachments-detail', kwargs={'pk': '2'})
        response = self.client.patch(url, {}, format='json')

        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    @patch('tracker.views.call_command')
    @patch.object(AttachmentFile, 'update_to_documentcloud')
    def test_update_attachment_title(self, mock_update_to_documentcloud, mock_call_command):
        admin_user = AdminUserFactory(username='Test admin user')
        token, _ = Token.objects.get_or_create(user=admin_user)

        attachment = AttachmentFileFactory(
            id=1,
            show=True,
            title='CR document',
            text_content='CHICAGO POLICE DEPARTMENT RD I HT334604',
            last_updated_by=None,
            allegation=AllegationFactory(crid='456'),
            url='http://foo.com',
            preview_image_url='https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            source_type='DOCUMENTCLOUD',
            file_type='document',
            pages=10,
            views_count=100,
            downloads_count=99,
            notifications_count=200,
            manually_updated=False,
        )
        attachment.created_at = datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc)
        attachment.save()

        url = reverse('api-v2:attachments-detail', kwargs={'pk': '1'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        with freeze_time('2017-08-05 12:00:01'):
            response = self.client.patch(url, {'title': 'New title'}, format='json')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 1,
            'crid': '456',
            'title': 'New title',
            'text_content': 'CHICAGO POLICE DEPARTMENT RD I HT334604',
            'url': 'http://foo.com',
            'preview_image_url': 'https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            'original_url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'created_at': '2017-08-04T09:30:00-05:00',
            'updated_at': '2017-08-05T07:00:01-05:00',
            'crawler_name': 'Document Cloud',
            'linked_documents': [],
            'pages': 10,
            'last_updated_by': 'Test admin user',
            'views_count': 100,
            'downloads_count': 99,
            'notifications_count': 200,
        })
        time.sleep(0.1)
        expect(mock_update_to_documentcloud).to.be.called_with('title', 'New title')
        updated_attachment = AttachmentFile.objects.get(pk=1)
        expect(updated_attachment.last_updated_by_id).to.eq(admin_user.id)
        expect(updated_attachment.manually_updated).to.be.true()
        expect(mock_call_command).to.be.called_with('clear_cache')

    @patch('tracker.views.call_command')
    @patch.object(AttachmentFile, 'update_to_documentcloud')
    def test_update_attachment_title_no_change(self, mock_update_to_documentcloud, mock_call_command):
        admin_user = AdminUserFactory(username='Test admin user')
        token, _ = Token.objects.get_or_create(user=admin_user)

        attachment = AttachmentFileFactory(
            id=1,
            show=True,
            title='No changed CR document',
            text_content='CHICAGO POLICE DEPARTMENT RD I HT334604',
            last_updated_by=None,
            allegation=AllegationFactory(crid='456'),
            url='http://foo.com',
            preview_image_url='https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            source_type='DOCUMENTCLOUD',
            file_type='document',
            pages=10,
            views_count=100,
            downloads_count=99,
            notifications_count=200,
            manually_updated=False,
        )
        attachment.created_at = datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc)
        attachment.save()

        url = reverse('api-v2:attachments-detail', kwargs={'pk': '1'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        with freeze_time('2017-08-05 12:00:01'):
            response = self.client.patch(url, {'title': 'No changed CR document'}, format='json')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 1,
            'crid': '456',
            'title': 'No changed CR document',
            'text_content': 'CHICAGO POLICE DEPARTMENT RD I HT334604',
            'url': 'http://foo.com',
            'preview_image_url': 'https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            'original_url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'created_at': '2017-08-04T09:30:00-05:00',
            'updated_at': '2017-08-05T07:00:01-05:00',
            'crawler_name': 'Document Cloud',
            'linked_documents': [],
            'pages': 10,
            'last_updated_by': None,
            'views_count': 100,
            'downloads_count': 99,
            'notifications_count': 200,
        })
        time.sleep(0.1)
        updated_attachment = AttachmentFile.objects.get(pk=1)
        expect(mock_update_to_documentcloud).not_to.be.called()
        expect(updated_attachment.last_updated_by_id).to.be.none()
        expect(updated_attachment.manually_updated).to.be.false()
        expect(mock_call_command).to.be.called_with('clear_cache')

    @patch('tracker.views.call_command')
    @patch.object(AttachmentFile, 'update_to_documentcloud')
    def test_update_attachment_text_content(self, mock_update_to_documentcloud, mock_call_command):
        admin_user = AdminUserFactory(username='Test admin user')
        token, _ = Token.objects.get_or_create(user=admin_user)

        attachment = AttachmentFileFactory(
            id=1,
            show=True,
            title='CR document',
            text_content='CHICAGO POLICE DEPARTMENT RD I HT334604',
            last_updated_by=None,
            allegation=AllegationFactory(crid='456'),
            url='http://foo.com',
            preview_image_url='https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            source_type='DOCUMENTCLOUD',
            file_type='document',
            pages=10,
            views_count=100,
            downloads_count=99,
            notifications_count=200,
            manually_updated=False,
        )
        attachment.created_at = datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc)
        attachment.save()

        url = reverse('api-v2:attachments-detail', kwargs={'pk': '1'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        with freeze_time('2017-08-05 12:00:01'):
            response = self.client.patch(
                url,
                {'text_content': 'New text content'},
                format='json'
            )

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 1,
            'crid': '456',
            'title': 'CR document',
            'text_content': 'New text content',
            'url': 'http://foo.com',
            'preview_image_url': 'https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            'original_url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'created_at': '2017-08-04T09:30:00-05:00',
            'updated_at': '2017-08-05T07:00:01-05:00',
            'crawler_name': 'Document Cloud',
            'linked_documents': [],
            'pages': 10,
            'last_updated_by': 'Test admin user',
            'views_count': 100,
            'downloads_count': 99,
            'notifications_count': 200,
        })
        time.sleep(0.1)
        updated_attachment = AttachmentFile.objects.get(pk=1)
        expect(mock_update_to_documentcloud).not_to.be.called()
        expect(updated_attachment.last_updated_by).to.eq(admin_user)
        expect(updated_attachment.manually_updated).to.be.true()
        expect(mock_call_command).to.be.called_with('clear_cache')

    @freeze_time('2017-01-14 12:00:01')
    def test_attachments_filtered_by_cr(self):
        allegation1 = AllegationFactory(crid='1')
        allegation2 = AllegationFactory(crid='2')

        AttachmentFileFactory(
            id=1,
            file_type='document',
            title='CRID 1051117 CR',
            source_type='DOCUMENTCLOUD',
            preview_image_url='http://web.com/image/CRID-1051117-CR-p1-normal.gif',
            views_count=1,
            downloads_count=1,
            allegation=allegation1
        )
        AttachmentFileFactory(
            id=2,
            file_type='audio',
            title='Log 1087021 911',
            source_type='COPA',
            preview_image_url=None,
            views_count=2,
            downloads_count=2,
            allegation=allegation2
        )

        base_url = reverse('api-v2:attachments-list')
        query_string = urlencode({'crid': allegation1.crid})
        url = f'{base_url}?{query_string}'
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 1,
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
                    'downloads_count': 1,
                    'crid': '1',
                    'show': True,
                    'documents_count': 1
                }
            ]
        })

    def test_attachments_full_text_search(self):
        allegation = AllegationFactory(crid=111333)

        AttachmentFileFactory(
            id=11,
            allegation=allegation)
        AttachmentFileFactory(
            id=22,
            title='hahaha')

        base_url = reverse('api-v2:attachments-list')

        response = self.client.get(f'{base_url}?match=11133')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['id']).to.eq(11)

        response = self.client.get(f'{base_url}?match=haha')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['id']).to.eq(22)

    def test_get_attachments_as_admin(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        AttachmentFileFactory(id=133, show=False)

        base_url = reverse('api-v2:attachments-list')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(base_url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['id']).to.eq(133)


class DocumentCrawlersViewSetTestCase(APITestCase):
    @override_settings(TIME_ZONE='UTC')
    def setUp(self):
        with freeze_time(datetime(2018, 3, 3, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=1,
                source_type='DOCUMENTCLOUD',
                status='Failed',
                num_documents=5,
                num_new_documents=1,
                num_updated_documents=4,
                num_successful_run=0
            )
        with freeze_time(datetime(2018, 4, 3, 12, 0, 1, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=2,
                source_type='DOCUMENTCLOUD',
                status='Success',
                num_documents=5,
                num_new_documents=1,
                num_updated_documents=4,
                num_successful_run=1
            )
        with freeze_time(datetime(2018, 3, 3, 12, 0, 10, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=3,
                source_type='PORTAL_COPA',
                status='Failed',
                num_documents=7,
                num_new_documents=1,
                num_updated_documents=5,
                num_successful_run=0
            )
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=4,
                source_type='PORTAL_COPA',
                status='Success',
                num_documents=6,
                num_new_documents=2,
                num_updated_documents=4,
                num_successful_run=1
            )
        with freeze_time(datetime(2018, 3, 3, 12, 0, 20, tzinfo=pytz.utc)):
            DocumentCrawlerFactory(
                id=5,
                source_type='SUMMARY_REPORTS_COPA',
                status='Failed',
                num_documents=3,
                num_new_documents=1,
                num_updated_documents=1,
                num_successful_run=0
            )
        with freeze_time(datetime(2018, 4, 3, 12, 0, 20, tzinfo=pytz.utc)):
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
