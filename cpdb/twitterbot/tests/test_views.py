from django.urls import reverse
from django.test import override_settings

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from twitterbot.utils.cryptography import get_hash_token


class WebhookViewSetTestCase(APITestCase):
    @override_settings(TWITTER_CONSUMER_SECRET='abc')
    def test_crc_check_400(self):
        url = reverse('api-v2:twitter-webhook-list', kwargs={})
        response = self.client.get(url, {})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data.get('message')).to.eq('Error: crc_token is missing from request')

    @override_settings(TWITTER_CONSUMER_SECRET='abc')
    def test_crc_check(self):
        crc_token = 'crc_123'
        response_token = get_hash_token('abc', 'crc_123')
        url = reverse('api-v2:twitter-webhook-list', kwargs={})
        response = self.client.get(url, {'crc_token': crc_token})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data.get('response_token')).to.eq(response_token)

    @override_settings(TWITTER_CONSUMER_SECRET='abc')
    def test_webhook_validate_source(self):
        hash1 = get_hash_token('abc', '{"message":"hi"}')
        url = reverse('api-v2:twitter-webhook-list', kwargs={})
        self.client.credentials(HTTP_X_TWITTER_WEBHOOKS_SIGNATURE=hash1)
        response = self.client.post(url, {'message': 'hi'}, format='json')
        expect(response.status_code).to.eq(status.HTTP_200_OK)

    @override_settings(TWITTER_CONSUMER_SECRET='abc')
    def test_webhook_validate_source_400(self):
        hash2 = get_hash_token('def', '{"message":"hi"}')
        url = reverse('api-v2:twitter-webhook-list', kwargs={})
        self.client.credentials(HTTP_X_TWITTER_WEBHOOKS_SIGNATURE=hash2)
        response = self.client.post(url, {'message': 'hi'}, format='json')
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data.get('message')).to.eq('Cannot recognize the requesting source')
