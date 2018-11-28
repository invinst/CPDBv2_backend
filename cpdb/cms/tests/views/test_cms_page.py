from django.urls import reverse

from freezegun import freeze_time
from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from authentication.factories import AdminUserFactory
from cms.serializers import SlugPageSerializer
from cms.models import SlugPage
from cms.fields import RichTextField


class CMSPageViewSetTestCase(APITestCase):

    class MyPageSerializer(SlugPageSerializer):
        my_text = RichTextField(fake_value=['Citizens Police Data Project'], source='fields')

        class Meta:
            slug = 'my-page'
            model = SlugPage

    @freeze_time('2016-10-07')
    def setUp(self):

        with patch('cms.fields.generate_draft_block_key', return_value='abc12'):
            serializer = self.MyPageSerializer(data=self.MyPageSerializer().fake_data())
            serializer.is_valid()
            serializer.save()

        self.maxDiff = None

    @patch('cms.views.get_slug_page_serializer', return_value=MyPageSerializer)
    def test_update_slug_page_bad_request(self, _):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        url = reverse('api-v2:cms-page-detail', kwargs={'pk': 'my-page'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'my_text',
                'type': 'rich_text',
                'value': 'Collaborate With Us.'
            }
        ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'message': {
                'my_text': 'Value must be in raw content state format'
            }
        })

    @patch('cms.views.get_slug_page_serializer', return_value=MyPageSerializer)
    def test_update_slug_page(self, _):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        url = reverse('api-v2:cms-page-detail', kwargs={'pk': 'my-page'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'my_text',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'text changed',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            }
        ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['fields']), 1)
        response_data = {
            field['name']: field for field in response.data['fields']
        }
        self.assertEqual(
            response_data['my_text']['value']['blocks'][0]['text'],
            'text changed')

        self.assertEqual(
            SlugPage.objects.first().fields['my_text_value']['blocks'][0]['text'],
            'text changed')

    @patch('cms.views.get_slug_page_serializer', return_value=MyPageSerializer)
    def test_get_slug_page(self, _):
        url = reverse('api-v2:cms-page-detail', kwargs={'pk': 'my-page'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['fields']), 1)
        response_data = {
            field['name']: field for field in response.data['fields']
        }

        self.assertEqual(
            response_data['my_text'],
            {
                'name': 'my_text',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'Citizens Police Data Project',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
