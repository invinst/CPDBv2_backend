from django.core.urlresolvers import reverse

from freezegun import freeze_time
from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from authentication.factories import AdminUserFactory
from cms.serializers import LandingPageSerializer, ReportPageSerializer, FAQPageSerializer
from cms.models import SlugPage


class CMSPageViewSetTestCase(APITestCase):
    @freeze_time('2016-10-07')
    def setUp(self):
        with patch('cms.fields.generate_draft_block_key', return_value='abc12'):
            serializer = LandingPageSerializer(data=LandingPageSerializer().fake_data(vftg_link='https://google.com'))
            serializer.is_valid()
            serializer.save()

            for _ in range(10):
                report_serializer = ReportPageSerializer(data=ReportPageSerializer().fake_data())
                report_serializer.is_valid()
                report_serializer.save()

                faq_serializer = FAQPageSerializer(data=FAQPageSerializer().fake_data())
                faq_serializer.is_valid()
                faq_serializer.save()

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
        self.assertEqual(len(response.data['fields']), 17)
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
        self.assertEqual(len(response.data['fields']), 17)
        response_data = {
            field['name']: field for field in response.data['fields']
        }
        self.assertEqual(len(response_data['reports']['value']), 8)
        self.assertEqual(len(response_data['faqs']['value']), 5)
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
                        },
                        {
                            'id': 3,
                            'name': 'Last starred entries only'
                        }
                    ]
                }
            })
        self.assertEqual(
            response_data['vftg_header'],
            {
                'name': 'vftg_header',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'CPDP WEEKLY',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
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
            response_data['hero_title'],
            {
                'name': 'hero_title',
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
                                'The Citizens Police Data Project collects and publishes '
                                'information about police accountability in Chicago.'),
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['hero_complaint_text'],
            {
                'name': 'hero_complaint_text',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'Explore Complaints against police officers',
                            'type': 'unstyled'
                        }
                    ],
                    'entityMap': {}
                }
            })
        self.assertEqual(
            response_data['hero_use_of_force_text'],
            {
                'name': 'hero_use_of_force_text',
                'type': 'rich_text',
                'value': {
                    'blocks': [
                        {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': 'abc12',
                            'text': 'View Use of Force incidents by police officers',
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
