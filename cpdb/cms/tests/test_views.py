from django.core.urlresolvers import reverse

from freezegun import freeze_time
from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from authentication.factories import AdminUserFactory
from cms.serializers import LandingPageSerializer, ReportPageSerializer, FAQPageSerializer
from cms.models import ReportPage, SlugPage, FAQPage


class CMSPageViewSetTestCase(APITestCase):
    @freeze_time('2016-10-07')
    def setUp(self):
        with patch('cms.fields.generate_draft_block_key', return_value='abc12'):
            serializer = LandingPageSerializer(data=LandingPageSerializer().fake_data(vftg_link='https://google.com'))
            serializer.is_valid()
            serializer.save()

        self.maxDiff = None

    def test_update_landing_page_bad_request(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        url = reverse('api-v2:cms-page-detail', kwargs={'pk': 'landing-page'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'collaborate_header',
                'type': 'rich_text',
                'value': 'Collaborate With Us.'
            }
        ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'message': {
                'collaborate_header': 'Value must be in raw content state format'
            }
        })

    def test_update_landing_page(self):
        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)

        url = reverse('api-v2:cms-page-detail', kwargs={'pk': 'landing-page'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(url, {'fields': [
            {
                'name': 'vftg_date',
                'type': 'date',
                'value': '2016-11-05'
            }
        ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['fields']), 13)
        response_data = {
            field['name']: field for field in response.data['fields']
        }
        self.assertEqual(
            response_data['vftg_date']['value'],
            '2016-11-05')

        self.assertEqual(
            SlugPage.objects.first().fields['vftg_date_value'],
            '2016-11-05')

    def test_get_landing_page(self):
        url = reverse('api-v2:cms-page-detail', kwargs={'pk': 'landing-page'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['fields']), 13)
        response_data = {
            field['name']: field for field in response.data['fields']
        }
        self.assertEqual(
            response_data['reporting_header'],
            {
                'name': 'reporting_header',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'Recent Reports',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['reporting_randomizer'],
            {
                'name': 'reporting_randomizer',
                'type': 'randomizer',
                'value': {
                    'poolSize': 10,
                    'selectedStrategyId': 1,
                    'strategies': [
                        {
                            'id': 1,
                            'name': 'Last entries'
                        },
                        {
                            'id': 2,
                            'name': 'Last days'
                        }
                    ]
                }
            })
        self.assertEqual(
            response_data['faq_header'],
            {
                'name': 'faq_header',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'FAQ',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['faq_randomizer'],
            {
                'name': 'faq_randomizer',
                'type': 'randomizer',
                'value': {
                    'poolSize': 10,
                    'selectedStrategyId': 1,
                    'strategies': [
                        {
                            'id': 1,
                            'name': 'Last entries'
                        },
                        {
                            'id': 2,
                            'name': 'Last days'
                        }
                    ]
                }
            })
        self.assertEqual(
            response_data['vftg_date'],
            {
                'name': 'vftg_date',
                'type': 'date',
                'value': '2016-10-07'
            })
        self.assertEqual(
            response_data['vftg_link'],
            {
                'name': 'vftg_link',
                'type': 'link',
                'value': 'https://google.com'
            })
        self.assertEqual(
            response_data['vftg_content'],
            {
                'name': 'vftg_content',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'Real Independence for Police Oversight Agencies',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['collaborate_header'],
            {
                'name': 'collaborate_header',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'Collaborate',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['collaborate_content'],
            {
                'name': 'collaborate_content',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': (
                                'We are collecting and publishing information that sheds light on police misconduct.'),
                            'type': 'unstyled'
                        },
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': (
                                'If you have documents or datasets you would like to publish, '
                                'please email us, or learn more.'),
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['about_header'],
            {
                'name': 'about_header',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'About',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['about_content'],
            {
                'name': 'about_content',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': (
                                'The Citizens Police Data Project houses police disciplinary '
                                'information obtained from the City of Chicago.'),
                            'type': 'unstyled'
                        },
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': (
                                'The information and stories we have collected here are intended as a resource for '
                                'public oversight. Our aim is to create a new model of accountability between '
                                'officers and citizens.'),
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })


class ReportPageViewSetTestCase(APITestCase):
    def setUp(self):
        with patch('cms.fields.generate_draft_block_key', return_value='abc12'):
            serializer = ReportPageSerializer(data=ReportPageSerializer().fake_data(
                title='a', excerpt=['b', 'c'], publication='d',
                publish_date='2016-10-25', author='e', article_link='f'))
            serializer.is_valid()
            serializer.save()
        self.maxDiff = None

    def test_list_report_page(self):
        url = reverse('api-v2:report-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        [report] = ReportPage.objects.all()
        actual_data = dict(response.data)
        fields = {
            field['name']: field for field in actual_data['results'][0]['fields']
        }

        self.assertEqual(len(fields.keys()), 6)
        self.assertEqual(actual_data['count'], 1)
        self.assertEqual(actual_data['next'], None)
        self.assertEqual(actual_data['previous'], None)
        self.assertEqual(actual_data['results'][0]['id'], report.id)

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


class FAQPageViewSetTestCase(APITestCase):
    def setUp(self):
        with patch('cms.fields.generate_draft_block_key', return_value='abc12'):
            serializer = FAQPageSerializer(data=FAQPageSerializer().fake_data(
                question='a', answer=['b', 'c']))
            serializer.is_valid()
            serializer.save()
        self.maxDiff = None

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
