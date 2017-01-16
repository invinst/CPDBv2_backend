from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect


class LandingPageViewSetTestCase(APITestCase):
    def test_list(self):
        url = reverse('api:landing-page-list')
        response = self.client.get(url)
        expect(response.status_code).to.be.equal(status.HTTP_200_OK)
