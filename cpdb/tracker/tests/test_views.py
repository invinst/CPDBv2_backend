from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from robber import expect
from freezegun import freeze_time
from urllib.parse import urlencode

from authentication.factories import AdminUserFactory
from data.factories import AttachmentFileFactory, AllegationFactory


class AttachmentAPITestCase(APITestCase):
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
        expect(response.data).to.eq({'show': False})

    def test_update_attachment_bad_request(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        AttachmentFileFactory(id=1)

        url = reverse('api-v2:attachments-detail', kwargs={'pk': '1'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {}, format='json')

        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)

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
