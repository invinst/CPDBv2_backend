from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect


class StatusViewsTestCase(APITestCase):
    def test_list(self):
        url = reverse('api-v2:status-list')
        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({'ok': True})
