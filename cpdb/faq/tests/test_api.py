import json

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from wagtail.wagtailcore.models import Page

from data.factories import RootPageFactory
from faq.factories import FAQPageFactory
from faq.models import FAQPage


class FAQAPITestCase(APITestCase):
    def test_list_faq(self):
        root = Page.add_root(instance=RootPageFactory.build())
        faq_1 = root.add_child(instance=FAQPageFactory.build(
            title='title a',
            body='[{"type": "paragraph", "value": "a a a a"}]'))

        faq_2 = root.add_child(instance=FAQPageFactory.build(
            title='title b',
            body='[{"type": "paragraph", "value": "b b b b"}]'))

        root.add_child(instance=FAQPageFactory.build(
            title='title c',
            body='[{"type": "paragraph", "value": "c c c c"}]'))

        url = reverse('api:faq-list')
        response = self.client.get(url, {'limit': 2})
        actual_content = json.loads(response.content)
        expected_results = [
            {
                'id': faq_1.id,
                'title': 'title a',
                'body': [
                    {
                        'type': 'paragraph',
                        'value': 'a a a a'
                    }
                ]
            },
            {
                'id': faq_2.id,
                'title': 'title b',
                'body': [
                    {
                        'type': 'paragraph',
                        'value': 'b b b b'
                    }
                ]
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(actual_content.get('results'), expected_results)
        self.assertEqual(actual_content.get('count'), 3)
        self.assertTrue('{url}?limit=2&offset=2'.format(url=str(url)) in actual_content.get('next'))

    def test_create_faq_success(self):
        self.assertEqual(FAQPage.objects.all().count(), 0)

        url = reverse('api:faq-list')
        response = self.client.post(url, {'title': 'title'})

        new_faq = FAQPage.objects.first()
        self.assertEqual(FAQPage.objects.first().title, 'title')

        actual_content = json.loads(response.content)
        expected_content = {
            'id': new_faq.id,
            'title': 'title',
            'body': []
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(actual_content, expected_content)

    def test_create_faq_failed(self):
        Page.add_root(instance=RootPageFactory.build())

        url = reverse('api:faq-list')
        response = self.client.post(url, {'title': ''})

        expected_content = {
            'title': ['This field cannot be blank.']
        }
        actual_content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(actual_content, expected_content)
