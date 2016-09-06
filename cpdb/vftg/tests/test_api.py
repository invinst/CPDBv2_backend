from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from mock import patch

from vftg.mailchimp_service import MailchimpAPIError


class VFTGAPITestCase(APITestCase):
    def test_subscribe_api_success(self):
        with patch('vftg.mailchimp_service.MailchimpService.subscribe', return_value=None):
            response = self.client.post(reverse('api:vftg-list'), {'email': 'john@doe.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': True})

    def test_subscribe_api_failure(self):
        with patch(
                'vftg.mailchimp_service.MailchimpService.subscribe',
                side_effect=MailchimpAPIError(400, 'email looks faked!')):
            response = self.client.post(reverse('api:vftg-list'), {'email': 'john@doe.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'success': False, 'detail': 'email looks faked!'})
