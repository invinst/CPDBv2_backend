from mock import patch

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect


class WebhookViewSetTestCase(APITestCase):
    @patch('twitterbot.views.get_hash_token', return_value='hash_abc')
    def test_crc_check(self, _):
        url = reverse('api-v2:twitter-webhook-list', kwargs={})
        response = self.client.get(url, {})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data.get('message')).to.eq('Error: crc_token is missing from request')

        url = reverse('api-v2:twitter-webhook-list', kwargs={})
        response = self.client.get(url, {'crc_token': 'crc_abc'})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data.get('response_token')).to.eq('hash_abc')

    @patch('twitterbot.views.hmac')
    @patch('twitterbot.views.get_hash_token', return_value='hash_abc')
    def test_webhook_validate_source(self, get_hash_token, hmac):
        hmac.compare_digest.return_value = True
        url = reverse('api-v2:twitter-webhook-list', kwargs={})
        self.client.credentials(HTTP_X_TWITTER_WEBHOOKS_SIGNATURE='hash_abc')
        response = self.client.post(url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        hmac.compare_digest.assert_called_with('hash_abc', 'hash_abc')

        hmac.compare_digest.return_value = False
        self.client.credentials(HTTP_X_TWITTER_WEBHOOKS_SIGNATURE='hash_def')
        response = self.client.post(url)
        hmac.compare_digest.assert_called_with('hash_def', 'hash_abc')
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data.get('message')).to.eq('Cannot recognize the requesting source')
