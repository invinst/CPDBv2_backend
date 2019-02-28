import time
from datetime import datetime
from operator import itemgetter
from urllib.parse import urlencode

import pytz
from django.urls import reverse
from freezegun import freeze_time
from mock import patch
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from robber import expect

from authentication.factories import AdminUserFactory
from data.factories import AttachmentFileFactory, AllegationFactory, UserFactory
from data.models import AttachmentFile


class DocumentTestCase(APITestCase):
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

    @freeze_time('2017-01-14 12:00:01')
    def test_list_attachments(self):
        AttachmentFileFactory(
            id=1,
            file_type='document',
            title='CRID 1051117 CR',
            source_type='DOCUMENTCLOUD',
            preview_image_url='http://web.com/image/CRID-1051117-CR-p1-normal.gif',
            views_count=1,
            downloads_count=1,
            show=True,
        )
        AttachmentFileFactory(
            id=2,
            file_type='audio',
            title='Log 1087021 911',
            source_type='COPA',
            preview_image_url=None,
            views_count=2,
            downloads_count=2,
            show=False,
        )
        AttachmentFileFactory(
            id=3,
            file_type='video',
            title='Log 1086127 Body Worn Camera #1',
            source_type='COPA',
            preview_image_url=None,
            views_count=3,
            downloads_count=3,
            show=True
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
                    'downloads_count': 1,
                    'show': True,
                },
                {
                    'id': 2,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'Log 1087021 911',
                    'source_type': 'COPA',
                    'preview_image_url': None,
                    'views_count': 2,
                    'downloads_count': 2,
                    'show': False,
                },
                {
                    'id': 3,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'Log 1086127 Body Worn Camera #1',
                    'source_type': 'COPA',
                    'preview_image_url': None,
                    'views_count': 3,
                    'downloads_count': 3,
                    'show': True,
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

        AttachmentFileFactory(id=1, show=True)

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

    @patch.object(AttachmentFile, 'update_to_documentcloud')
    def test_update_attachment_title(self, mock_update_to_documentcloud):
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

    @patch.object(AttachmentFile, 'update_to_documentcloud')
    def test_update_attachment_title_no_change(self, mock_update_to_documentcloud):
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

    @patch.object(AttachmentFile, 'update_to_documentcloud')
    def test_update_attachment_text_content(self, mock_update_to_documentcloud):
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
            show=True,
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
            show=False,
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
                    'show': True,
                }
            ]
        })
