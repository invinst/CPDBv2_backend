from datetime import datetime
from operator import itemgetter

import pytz
from django.test import override_settings
from django.urls import reverse
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
from activity_log.models import ActivityLog
from activity_log.constants import ADD_TAG_TO_DOCUMENT, REMOVE_TAG_FROM_DOCUMENT
from tracker.tests.mixins import TrackerTestCaseMixin


class AttachmentAPITestCase(TrackerTestCaseMixin, APITestCase):
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
            tags=['tag123']
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
            tags=['tag124'],
        )
        AttachmentFileFactory(
            id=125,
            allegation=allegation,
            show=True,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
            tags=['tag125'],
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
            tags=['tag127'],
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
            'tags': ['tag123'],
            'next_document_id': 126,
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
            url='http://document/link/1',
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
            url='http://audio/link/2',
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
            url='http://video/link/3',
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
                    'crid': '123',
                    'show': True,
                    'documents_count': 2,
                    'file_type': 'document',
                    'url': 'http://document/link/1',
                },
                {
                    'id': 2,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'Log 1087021 911',
                    'source_type': 'COPA',
                    'preview_image_url': None,
                    'crid': '123',
                    'show': True,
                    'documents_count': 2,
                    'file_type': 'audio',
                    'url': 'http://audio/link/2',
                },
                {
                    'id': 3,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'Log 1086127 Body Worn Camera #1',
                    'source_type': 'COPA',
                    'preview_image_url': None,
                    'crid': '456',
                    'show': True,
                    'documents_count': 1,
                    'file_type': 'video',
                    'url': 'http://video/link/3',
                }
            ]
        }

        url = reverse('api-v2:attachments-list', kwargs={})
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_data)

    @freeze_time('2017-01-14 12:00:01')
    def test_list_attachments_authenticated_user(self):
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
            url='http://document/link/1',
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
            url='http://audio/link/2',
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
            url='http://video/link/3',
        )
        AttachmentFileFactory(
            allegation=allegation2,
            id=4,
            file_type='video',
            title='Log 1086127 Body Worn Camera #1',
            source_type='COPA',
            preview_image_url=None,
            views_count=3,
            downloads_count=3,
            url='http://video/link/4',
            show=False
        )

        expected_data = {
            'count': 4,
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
                    'file_type': 'document',
                    'url': 'http://document/link/1',
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
                    'file_type': 'audio',
                    'url': 'http://audio/link/2',
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
                    'file_type': 'video',
                    'url': 'http://video/link/3',
                },
                {
                    'id': 4,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'Log 1086127 Body Worn Camera #1',
                    'source_type': 'COPA',
                    'preview_image_url': None,
                    'views_count': 3,
                    'downloads_count': 3,
                    'crid': '456',
                    'show': False,
                    'documents_count': 1,
                    'file_type': 'video',
                    'url': 'http://video/link/4',
                }
            ]
        }

        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        base_url = reverse('api-v2:attachments-list')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(base_url)

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

    def test_update_attachment_bad_request_with_error(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        AttachmentFileFactory(id=1)
        expected_data = {
            'message': {
                'tags': ['Ensure this field has no more than 20 characters.']
            }
        }

        url = reverse('api-v2:attachments-detail', kwargs={'pk': '1'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'tags': ['this is a tag with more than 20 characters']}, format='json')

        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq(expected_data)

    def test_update_attachment_with_invalid_pk(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        AttachmentFileFactory(id=1)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('api-v2:attachments-detail', kwargs={'pk': '2'})
        response = self.client.patch(url, {}, format='json')

        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_update_attachment_title(self):
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
            'tags': [],
            'next_document_id': None,
        })
        updated_attachment = AttachmentFile.objects.get(pk=1)
        expect(updated_attachment.last_updated_by_id).to.eq(admin_user.id)
        expect(updated_attachment.manually_updated).to.be.true()

    def test_update_attachment_tags(self):
        admin_user = AdminUserFactory(id=1, username='Test admin user')
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
            tags=['tag1']
        )
        attachment.created_at = datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc)
        attachment.save()

        url = reverse('api-v2:attachments-detail', kwargs={'pk': '1'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        with freeze_time('2017-08-05 12:00:01'):
            response = self.client.patch(url, {'tags': ['tag1', 'tag2', 'tag3']}, format='json')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 1,
            'crid': '456',
            'title': 'CR document',
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
            'tags': ['tag1', 'tag2', 'tag3'],
            'next_document_id': None,
        })
        updated_attachment = AttachmentFile.objects.get(pk=1)
        expect(updated_attachment.last_updated_by_id).to.eq(admin_user.id)
        expect(updated_attachment.manually_updated).to.be.true()

        activity_logs = ActivityLog.objects.all().order_by('data')
        expect(activity_logs.count()).to.eq(2)

        activity_log_1 = activity_logs[0]
        expect(activity_log_1.action_type).to.eq(ADD_TAG_TO_DOCUMENT)
        expect(activity_log_1.user_id).to.eq(1)
        expect(activity_log_1.data).to.eq('tag2')

        activity_log_2 = activity_logs[1]
        expect(activity_log_2.action_type).to.eq(ADD_TAG_TO_DOCUMENT)
        expect(activity_log_2.user_id).to.eq(1)
        expect(activity_log_2.data).to.eq('tag3')

    def test_remove_attachment_tags(self):
        admin_user = AdminUserFactory(id=1, username='Test admin user')
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
            tags=['tag1', 'tag2', 'tag3']
        )
        attachment.created_at = datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc)
        attachment.save()

        url = reverse('api-v2:attachments-detail', kwargs={'pk': '1'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        with freeze_time('2017-08-05 12:00:01'):
            response = self.client.patch(url, {'tags': ['tag1']}, format='json')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 1,
            'crid': '456',
            'title': 'CR document',
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
            'tags': ['tag1'],
            'next_document_id': None
        })
        updated_attachment = AttachmentFile.objects.get(pk=1)
        expect(updated_attachment.last_updated_by_id).to.eq(admin_user.id)
        expect(updated_attachment.manually_updated).to.be.true()

        activity_logs = ActivityLog.objects.all().order_by('data')
        expect(activity_logs.count()).to.eq(2)

        activity_log_1 = activity_logs[0]
        expect(activity_log_1.action_type).to.eq(REMOVE_TAG_FROM_DOCUMENT)
        expect(activity_log_1.user_id).to.eq(1)
        expect(activity_log_1.data).to.eq('tag2')

        activity_log_2 = activity_logs[1]
        expect(activity_log_2.action_type).to.eq(REMOVE_TAG_FROM_DOCUMENT)
        expect(activity_log_2.user_id).to.eq(1)
        expect(activity_log_2.data).to.eq('tag3')

    def test_update_attachment_title_no_change(self):
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
            'tags': [],
            'next_document_id': None,
        })
        updated_attachment = AttachmentFile.objects.get(pk=1)
        expect(updated_attachment.last_updated_by_id).to.be.none()
        expect(updated_attachment.manually_updated).to.be.false()

    def test_update_attachment_text_content(self):
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
            'tags': [],
            'next_document_id': None,
        })
        updated_attachment = AttachmentFile.objects.get(pk=1)
        expect(updated_attachment.last_updated_by).to.eq(admin_user)
        expect(updated_attachment.manually_updated).to.be.true()

    @freeze_time('2017-01-14 12:00:01')
    def test_attachments_filtered_by_cr_unauthenticated_user(self):
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
            allegation=allegation1,
            url='http://document/link/1',
        )
        AttachmentFileFactory(
            id=2,
            file_type='audio',
            title='Log 1087021 911',
            source_type='COPA',
            preview_image_url=None,
            views_count=2,
            downloads_count=2,
            allegation=allegation2,
            url='http://audio/link/2',
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
                    'crid': '1',
                    'show': True,
                    'documents_count': 1,
                    'file_type': 'document',
                    'url': 'http://document/link/1',
                }
            ]
        })

    @freeze_time('2017-01-14 12:00:01')
    def test_attachments_filtered_by_cr_authenticated_user(self):
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
            allegation=allegation1,
            url='http://document/link/1',
        )
        AttachmentFileFactory(
            id=2,
            file_type='audio',
            title='Log 1087021 911',
            source_type='COPA',
            preview_image_url=None,
            views_count=2,
            downloads_count=2,
            allegation=allegation2,
            url='http://audio/link/2',
        )
        AttachmentFileFactory(
            id=3,
            file_type='document',
            title='CRID 1051117 CR',
            source_type='DOCUMENTCLOUD',
            preview_image_url='http://web.com/image/CRID-1051117-CR-p1-normal.gif',
            views_count=1,
            downloads_count=1,
            allegation=allegation1,
            url='http://document/link/3',
            show=False,
        )

        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        base_url = reverse('api-v2:attachments-list')
        query_string = urlencode({'crid': allegation1.crid})
        url = f'{base_url}?{query_string}'
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 2,
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
                    'documents_count': 1,
                    'file_type': 'document',
                    'url': 'http://document/link/1',
                },
                {
                    'id': 3,
                    'created_at': '2017-01-14T06:00:01-06:00',
                    'title': 'CRID 1051117 CR',
                    'source_type': 'DOCUMENTCLOUD',
                    'preview_image_url': 'http://web.com/image/CRID-1051117-CR-p1-normal.gif',
                    'views_count': 1,
                    'downloads_count': 1,
                    'crid': '1',
                    'show': False,
                    'documents_count': 1,
                    'file_type': 'document',
                    'url': 'http://document/link/3',
                }
            ]
        })

    @freeze_time('2017-01-14 12:00:01')
    def test_attachments_full_text_search(self):
        allegation_1 = AllegationFactory(crid=111333)
        allegation_2 = AllegationFactory(crid=123456)

        AttachmentFileFactory(
            id=11,
            allegation=allegation_1,
            show=True,
        )
        AttachmentFileFactory(
            id=22,
            title='summary report',
            show=True,
        )
        AttachmentFileFactory(
            id=33,
            title='document title',
            text_content='document content',
            show=True,
        )
        AttachmentFileFactory(
            id=44,
            title='This is a title',
            text_content='This is a content.',
            source_type='DOCUMENTCLOUD',
            allegation=allegation_2,
            show=True,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )

        AttachmentFileFactory(
            id=55,
            allegation=allegation_1,
            show=False,
        )
        AttachmentFileFactory(
            id=66,
            title='summary report',
            show=False,
        )
        AttachmentFileFactory(
            id=77,
            title='document title',
            text_content='document content',
            show=False,
        )
        AttachmentFileFactory(
            id=88,
            title='This is a title',
            text_content='This is a content.',
            show=False,
        )

        base_url = reverse('api-v2:attachments-list')
        self.refresh_index()

        response = self.client.get(f'{base_url}?match=11133')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['id']).to.eq(11)

        response = self.client.get(f'{base_url}?match=summary')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['id']).to.eq(22)

        response = self.client.get(f'{base_url}?match=document')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]['id']).to.eq(33)

        response = self.client.get(f'{base_url}?crid=123456')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(1)

        expect(response.data['results'][0]).to.eq({
            'id': 44,
            'created_at': '2017-01-14T06:00:01-06:00',
            'title': 'This is a title',
            'source_type': 'DOCUMENTCLOUD',
            'crid': '123456',
            'show': True,
            'file_type': 'document',
            'url': 'https://www.documentcloud.org/documents/1-CRID-123-CR.html',
            'preview_image_url': 'https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            'documents_count': 1,
        })

    def test_attachments_full_text_search_match_multiple_fields(self):
        allegation = AllegationFactory(crid=123456)

        AttachmentFileFactory(
            id=11,
            allegation=allegation
        )
        AttachmentFileFactory(
            id=22,
            title='Title 123456'
        )
        AttachmentFileFactory(
            id=33,
            title='document title',
            text_content='document content 123456'
        )
        AttachmentFileFactory(
            id=44,
            title='document title',
            text_content='document content'
        )

        expected_ids = [11, 22, 33]

        base_url = reverse('api-v2:attachments-list')
        self.refresh_index()

        response = self.client.get(f'{base_url}?match=12345')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(3)
        expect(expected_ids).to.contain(*[result['id'] for result in response.data['results']])

    def test_attachments_full_text_search_with_pagination(self):
        allegation = AllegationFactory(crid=111333)

        AttachmentFileFactory(
            id=11,
            title='summary',
            allegation=allegation
        )
        AttachmentFileFactory(
            id=22,
            title='summary report'
        )
        AttachmentFileFactory(
            id=33,
            title='summary report title',
            text_content='document content'
        )

        base_url = reverse('api-v2:attachments-list')
        self.refresh_index()

        response = self.client.get(f'{base_url}?match=summary&limit=2&offset=2')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(3)
        expect(response.data['next']).to.be.none()
        expect(response.data['previous']).to.contain(f'{base_url}?limit=2&match=summary')
        expect(len(response.data['results'])).to.eq(1)

    def test_attachments_full_text_search_as_admin(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        AttachmentFileFactory(
            id=11,
            title='document title 1',
            text_content='document content 1',
            show=True,
        )
        AttachmentFileFactory(
            id=22,
            title='document title 2',
            text_content='document content 2',
            show=False,
        )
        AttachmentFileFactory(
            id=33,
            title='this is title',
            text_content='this is content',
            show=False,
        )

        base_url = reverse('api-v2:attachments-list')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        expected_ids = [11, 22]

        self.refresh_index()
        response = self.client.get(f'{base_url}?match=document')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(2)
        expect(expected_ids).to.contain(*[result['id'] for result in response.data['results']])

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

    def test_tags(self):
        AttachmentFileFactory(tags=['chicago', 'tactical'])
        AttachmentFileFactory(tags=['tactical', 'twitter', 'another tag'])
        AttachmentFileFactory(tags=[])
        url = reverse('api-v2:attachments-tags')
        response = self.client.get(url)
        expect(response.data).to.eq(['another tag', 'chicago', 'tactical', 'twitter'])


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
