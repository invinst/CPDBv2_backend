from django.test import SimpleTestCase

from mock import patch

from twitterbot.webhook_manager import WebhookManager


class WebhookManagerTestCase(SimpleTestCase):
    def setUp(self):
        self.manager = WebhookManager('auth')
        self.manager.endpoint = '%s/webhooks.json'
        self.manager.single_endpoint = '%s/webhooks/%s.json'

    @patch('twitterbot.webhook_manager.requests.get')
    def test_all(self, get):
        self.manager.all()
        get.assert_called_once_with(
            url='test/webhooks.json',
            auth='auth'
        )

    @patch('twitterbot.webhook_manager.requests.post')
    def test_register(self, post):
        self.manager.register('webhook_url')
        post.assert_called_once_with(
            url='test/webhooks.json',
            params={'url': 'webhook_url'},
            auth='auth'
        )

    @patch('twitterbot.webhook_manager.requests.delete')
    def test_remove(self, delete):
        self.manager.remove(123)
        delete.assert_called_once_with(
            url='test/webhooks/123.json',
            auth='auth'
        )
