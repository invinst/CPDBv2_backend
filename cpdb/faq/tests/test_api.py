import json

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from wagtail.wagtailcore.models import Page

from faq.factories import FAQPageFactory
from faq.models import FAQPage


class FAQAPITestCase(APITestCase):
    def setUp(self):
        FAQPage.get_tree().all().delete()

    def test_list_faq(self):
        root = FAQPage.add_root(
            instance=Page(title='Root', slug='root', content_type=ContentType.objects.get_for_model(Page)))

        faq_page_1 = root.add_child(
            instance=FAQPageFactory.build(
                title='title a',
                body='[{"type": "paragraph", "value": "a a a a"}]'
                ))

        faq_page_2 = root.add_child(
            instance=FAQPageFactory.build(
                title='title b',
                body='[{"type": "paragraph", "value": "b b b b"}]'
                ))

        root.add_child(
            instance=FAQPageFactory.build(
                title='title c',
                body='[{"type": "paragraph", "value": "c c c c"}]'
                ))

        url = reverse('api:faq-list')
        response = self.client.get(url, {'limit': 2})
        actual_content = json.loads(response.content)
        expected_results = [
            {
                'id': faq_page_1.id,
                'title': 'title a',
                'body': [
                    {
                        'type': 'paragraph',
                        'value': 'a a a a'
                    }
                ]
            },
            {
                'id': faq_page_2.id,
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
