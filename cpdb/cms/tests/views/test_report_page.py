from django.core.urlresolvers import reverse

from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from authentication.factories import AdminUserFactory
from cms.serializers import ReportPageSerializer
from cms.models import ReportPage


class ReportPageViewSetTestCase(APITestCase):
    def setUp(self):
        with patch('cms.fields.generate_draft_block_key', return_value='abc12'):
            serializer = ReportPageSerializer(data=ReportPageSerializer().fake_data(
                title='a', excerpt=['b', 'c'], publication='d',
                publish_date='2016-10-25', author='e', article_link='f'))
            serializer.is_valid()
            serializer.save()

            serializer2 = ReportPageSerializer(data=ReportPageSerializer().fake_data())
            serializer2.is_valid()
            serializer2.save()
        self.maxDiff = None

    def test_retrieve_report_page(self):
        report = ReportPage.objects.first()
        url = reverse('api-v2:report-detail', kwargs={'pk': report.id})

        response = self.client.get(url)
        actual_data = dict(response.data)
        fields = {
            field['name']: field for field in actual_data['fields']
        }
        self.assertEqual(actual_data['id'], report.id)
        self.assertDictEqual(fields['author'], {
            'name': 'author',
            'type': 'string',
            'value': 'e'
        })
        self.assertDictEqual(fields['publication'], {
            'name': 'publication',
            'type': 'string',
            'value': 'd'
        })
        self.assertDictEqual(fields['publish_date'], {
            'name': 'publish_date',
            'type': 'date',
            'value': '2016-10-25'
        })
        self.assertDictEqual(fields['excerpt'], {
            'name': 'excerpt',
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
        self.assertDictEqual(fields['title'], {
            'name': 'title',
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
        self.assertDictEqual(fields['article_link'], {
            'name': 'article_link',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'f',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })

    def test_list_report_page(self):
        url = reverse('api-v2:report-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        [report1, report2] = ReportPage.objects.all().order_by('created')
        actual_data = dict(response.data)

        self.assertEqual(actual_data['results'][0]['id'], report2.id)
        self.assertEqual(actual_data['results'][1]['id'], report1.id)
        fields = {
            field['name']: field for field in actual_data['results'][1]['fields']
        }

        self.assertEqual(len(fields.keys()), 6)
        self.assertEqual(actual_data['count'], 2)
        self.assertEqual(actual_data['next'], None)
        self.assertEqual(actual_data['previous'], None)

        self.assertDictEqual(fields['author'], {
            'name': 'author',
            'type': 'string',
            'value': 'e'
        })
        self.assertDictEqual(fields['publication'], {
            'name': 'publication',
            'type': 'string',
            'value': 'd'
        })
        self.assertDictEqual(fields['publish_date'], {
            'name': 'publish_date',
            'type': 'date',
            'value': '2016-10-25'
        })
        self.assertDictEqual(fields['excerpt'], {
            'name': 'excerpt',
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
        self.assertDictEqual(fields['title'], {
            'name': 'title',
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
        self.assertDictEqual(fields['article_link'], {
            'name': 'article_link',
            'type': 'rich_text',
            'value': {
                'blocks': [
                    {
                        'data': {},
                        'depth': 0,
                        'entityRanges': [],
                        'inlineStyleRanges': [],
                        'key': 'abc12',
                        'text': 'f',
                        'type': 'unstyled'
                    }
                ],
                'entityMap': {}
            }
        })

    def test_update_report_page_bad_request(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        report_page = ReportPage.objects.first()

        url = reverse('api-v2:report-detail', kwargs={'pk': report_page.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'title',
                'type': 'rich_text',
                'value': 'new title'
            }
        ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'message': {
                'title': 'Value must be in raw content state format'
            }
        })

    def test_update_report_page(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        report_page = ReportPage.objects.first()

        url = reverse('api-v2:report-detail', kwargs={'pk': report_page.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'publication',
                'type': 'string',
                'value': 'new york times'
            }
        ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['fields']), 6)
        response_data = {
            field['name']: field for field in response.data['fields']
        }
        self.assertEqual(
            response_data['publication']['value'],
            'new york times')
        report_page.refresh_from_db()
        self.assertEqual(
            report_page.fields['publication_value'],
            'new york times')

    def test_add_report_bad_request(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('api-v2:report-list')
        response = self.client.post(url, {
            'fields': [{
                'name': 'title',
                'type': 'rich_text',
                'value': 'a'
            }, {
                'name': 'excerpt',
                'type': 'rich_text',
                'value': {
                    'blocks': 'c',
                    'entityMap': 'd'
                }
            }, {
                'name': 'publication',
                'type': 'string',
                'value': 'ccc'
            }, {
                'name': 'publish_date',
                'type': 'date',
                'value': '1900-01-01'
            }, {
                'name': 'author',
                'type': 'string',
                'value': 'ddd'
            }]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'message': {
                'title': 'Value must be in raw content state format'
            }
        })

    def test_add_report(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('api-v2:report-list')
        response = self.client.post(url, {
            'fields': [{
                'name': 'title',
                'type': 'rich_text',
                'value': {
                    'blocks': 'a',
                    'entityMap': 'b'
                }
            }, {
                'name': 'excerpt',
                'type': 'rich_text',
                'value': {
                    'blocks': 'c',
                    'entityMap': 'd'
                }
            }, {
                'name': 'publication',
                'type': 'string',
                'value': 'ccc'
            }, {
                'name': 'publish_date',
                'type': 'date',
                'value': '1900-01-01'
            }, {
                'name': 'author',
                'type': 'string',
                'value': 'ddd'
            }]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_report = ReportPage.objects.last()
        self.assertDictEqual(created_report.fields, {
            'title_value': {
                'blocks': 'a',
                'entityMap': 'b'
            },
            'title_type': 'rich_text',
            'excerpt_value': {
                'blocks': 'c',
                'entityMap': 'd'
            },
            'excerpt_type': 'rich_text',
            'publication_value': 'ccc',
            'publication_type': 'string',
            'publish_date_value': '1900-01-01',
            'publish_date_type': 'date',
            'author_value': 'ddd',
            'author_type': 'string'
        })
