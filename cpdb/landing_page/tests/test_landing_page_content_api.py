import json

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from landing_page.factories import LandingPageContentFactory


class LandingPageContentAPITestCase(APITestCase):
    def setUp(self):
        self.landing_page_content = LandingPageContentFactory()

    def test_get_api(self):
        url = reverse('api-v2:landing-page-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actual_content = json.loads(response.content)

        self.assertEqual(actual_content, {
            'collaborate_header': self.landing_page_content.collaborate_header,
            'collaborate_content': self.landing_page_content.collaborate_content,
            'id': self.landing_page_content.id
            })

    def test_update_api(self):
        url = reverse('api-v2:landing-page-list')
        response = self.client.post(url, {
            'collaborate_header': 'a',
            'collaborate_content': {'a': 'b'}
            }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actual_content = json.loads(response.content)
        self.assertEqual(actual_content, {
            'collaborate_header': 'a',
            'collaborate_content': {'a': 'b'},
            'id': self.landing_page_content.pk
            })

        self.landing_page_content.refresh_from_db()
        self.assertEqual(self.landing_page_content.collaborate_header, 'a')
