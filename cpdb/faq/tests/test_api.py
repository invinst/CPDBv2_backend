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

    def create_root(self):
        content_type = ContentType.objects.get_for_model(Page)
        root = FAQPage.add_root(
            instance=Page(title='Root', slug='root', content_type=content_type))
        home_page = root.add_child(instance=Page(title='Home', slug='home', content_type=content_type))
        return (root, home_page)

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

    def test_create_faq_success(self):
        (root, home_page) = self.create_root()

        url = reverse('api:faq-list')
        response = self.client.post(url, {'title': 'title'})

        home_page.refresh_from_db()
        new_faq_page = home_page.get_first_child()

        self.assertEqual(new_faq_page.title, 'title')

        actual_content = json.loads(response.content)
        expected_content = {
            'id': new_faq_page.id,
            'title': 'title',
            'body': []
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(actual_content, expected_content)

    def test_create_faq_failed(self):
        (root, home_page) = self.create_root()

        url = reverse('api:faq-list')
        response = self.client.post(url, {'title': ''})

        expected_content = {
            'title': ['This field cannot be blank.']
        }
        actual_content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(actual_content, expected_content)
