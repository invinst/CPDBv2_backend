from django.test import TestCase
from django.urls import reverse

from robber import expect


class UrlsTestCase(TestCase):
    def test_index_redirect(self):
        response = self.client.get(reverse('index_redirect'))
        expect(response.status_code).to.eq(301)
        expect(response.url).to.eq('/')

    def test_admin_redirect(self):
        response = self.client.get(reverse('admin_redirect'))
        expect(response.status_code).to.eq(301)
        expect(response.url).to.eq('/admin/')
