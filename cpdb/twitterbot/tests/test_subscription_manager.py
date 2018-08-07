from django.test import SimpleTestCase

from robber import expect
from mock import patch

from twitterbot.subscription_manager import SubscriptionsManager


class SubscriptionManagerTestCase(SimpleTestCase):
    def setUp(self):
        self.manager = SubscriptionsManager(
            'consumer_key',
            'consumer_secret'
        )
        self.manager.list_endpoint = 'list.api'
        self.manager.endpoint = 'main.api'

    def test_set_environment_name(self):
        self.manager.set_environment_name('dev')
        expect(self.manager.list_endpoint)\
            .to.eq('https://api.twitter.com/1.1/account_activity/all/dev/subscriptions/list.json')
        expect(self.manager.endpoint)\
            .to.eq('https://api.twitter.com/1.1/account_activity/all/dev/subscriptions.json')

    @patch('twitterbot.subscription_manager.requests.get')
    def test_all(self, get):
        self.manager.all('bearer_abc')
        get.assert_called_once_with(
            url='list.api',
            headers={'Authorization': 'Bearer bearer_abc'}
        )

    @patch('twitterbot.subscription_manager.requests.post')
    @patch('twitterbot.subscription_manager.OAuth1', return_value='auth')
    def test_add(self, _, post):
        self.manager.add('token_abc', 'token_abc_secret')
        post.assert_called_once_with(
            url='main.api',
            auth='auth'
        )

    @patch('twitterbot.subscription_manager.requests.delete')
    @patch('twitterbot.subscription_manager.OAuth1', return_value='auth')
    def test_remove(self, _, delete):
        self.manager.remove('token_abc', 'token_abc_secret')
        delete.assert_called_once_with(
            url='main.api',
            auth='auth'
        )
