from mock import patch

from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect


class FAQViewSetTestCase(APITestCase):
    def test_create_success(self):
        response = self.client.post(reverse('api:faq-list'), {
            'title': 'title'
        })
        expect(response.status_code).to.be.equal(status.HTTP_201_CREATED)

    @patch('wagtail.wagtailcore.models.Page.add_child')
    def test_create_failure(self, add_child):
        add_child.side_effect = DjangoValidationError({'title': 'value'})

        response = self.client.post(reverse('api:faq-list'), {
            'title': 'title'
        })

        expect(response.status_code).to.be.equal(status.HTTP_400_BAD_REQUEST)
