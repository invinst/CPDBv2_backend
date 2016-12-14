from django.core.urlresolvers import reverse

from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from authentication.factories import AdminUserFactory
from cms.serializers import FAQPageSerializer
from cms.models import FAQPage


class FAQPageViewSetTestCase(APITestCase):
    def setUp(self):
        with patch('cms.fields.generate_draft_block_key', return_value='abc12'):
            serializer = FAQPageSerializer(data=FAQPageSerializer().fake_data(
                question='a', answer=['b', 'c']))
            serializer.is_valid()
            serializer.save()
        self.maxDiff = None

    def test_retrieve(self):
        [faq_page] = FAQPage.objects.all()
        url = reverse('api-v2:faq-detail', kwargs={'pk': faq_page.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actual_data = dict(response.data)

        self.assertEqual(actual_data['id'], faq_page.id)
        fields = {
            field['name']: field for field in actual_data['fields']
        }
        self.assertDictEqual(fields['answer'], {
            'name': 'answer',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'b',
                        'type': 'unstyled'
                    },
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'c',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })
        self.assertDictEqual(fields['question'], {
            'name': 'question',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'a',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })

    def test_list(self):
        url = reverse('api-v2:faq-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        [faq] = FAQPage.objects.all()
        actual_data = dict(response.data)
        fields = {
            field['name']: field for field in actual_data['results'][0]['fields']
        }

        self.assertEqual(actual_data['count'], 1)
        self.assertEqual(actual_data['next'], None)
        self.assertEqual(actual_data['previous'], None)
        self.assertEqual(actual_data['results'][0]['id'], faq.id)
        self.assertDictEqual(fields['answer'], {
            'name': 'answer',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'b',
                        'type': 'unstyled'
                    },
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'c',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })
        self.assertDictEqual(fields['question'], {
            'name': 'question',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'a',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })

    def test_update_bad_request(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        faq_page = FAQPage.objects.first()

        url = reverse('api-v2:faq-detail', kwargs={'pk': faq_page.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'question',
                'type': 'rich_text',
                'value': 'abc'
            }
        ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'message': {
                'question': 'Value must be in raw content state format'
            }
        })

    def test_update(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        faq_page = FAQPage.objects.first()

        url = reverse('api-v2:faq-detail', kwargs={'pk': faq_page.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'question',
                'type': 'rich_text',
                'value': {
                    'blocks': 'a',
                    'entityMap': 'b'
                }
            }
        ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['fields']), 2)
        response_data = {
            field['name']: field for field in response.data['fields']
        }
        self.assertEqual(
            response_data['question']['value'],
            {
                'blocks': 'a',
                'entityMap': 'b'
            })
        faq_page.refresh_from_db()
        self.assertEqual(
            faq_page.fields['question_value'],
            {
                'blocks': 'a',
                'entityMap': 'b'
            })

    def test_create(self):
        url = reverse('api-v2:faq-list')
        response = self.client.post(url, {
            'fields': [{
                'name': 'question',
                'type': 'rich_text',
                'value': {
                    'blocks': 'a',
                    'entityMap': 'b'
                }
            }]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_faq = FAQPage.objects.last()
        self.assertDictEqual(created_faq.fields, {
            'question_value': {
                'blocks': 'a',
                'entityMap': 'b'
            },
            'question_type': 'rich_text'
        })

    def test_create_with_answer(self):
        url = reverse('api-v2:faq-list')
        response = self.client.post(url, {
            'fields': [{
                'name': 'answer',
                'type': 'rich_text',
                'value': {
                    'blocks': 'a',
                    'entityMap': 'b'
                }
            }]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data['message'], {'non_field_errors': ['Unauthorized user cannot add answer.']})

    def test_authorized_create(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('api-v2:faq-list')
        response = self.client.post(url, {
            'fields': [{
                'name': 'question',
                'type': 'rich_text',
                'value': {
                    'blocks': 'a',
                    'entityMap': 'b'
                }
            }, {
                'name': 'answer',
                'type': 'rich_text',
                'value': {
                    'blocks': 'c',
                    'entityMap': 'd'
                }
            }]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
