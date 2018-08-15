from django.test import SimpleTestCase

from robber import expect
from mock import Mock, patch

from twitterbot.twitter_client import TwitterClient


class TweetTestCase(SimpleTestCase):
    def setUp(self):
        self.client = TwitterClient(
            consumer_key='consumer_key',
            consumer_secret='consumer_secret',
            app_token_key='app_token_key',
            app_token_secret='app_token_secret'
        )

    def test_webhook(self):
        self.client._webhook = 'webhook'
        expect(self.client.webhook).to.eq('webhook')

    def test_subscription(self):
        self.client._subscription = 'subscription'
        expect(self.client.subscription).to.eq('subscription')

    @patch('twitterbot.twitter_client.HTTPBasicAuth', return_value='auth')
    @patch('twitterbot.twitter_client.OAuth2Session')
    def test_get_bear_token(self, OAuth2Session, HTTPBasicAuth):
        oauth_mock = OAuth2Session()
        oauth_mock.fetch_token = Mock(return_value={'access_token': 'abc'})
        token = self.client.get_bearer_token()
        oauth_mock.fetch_token.assert_called_once_with(
            token_url='https://api.twitter.com/oauth2/token',
            auth='auth'
        )
        expect(token).to.eq('abc')

    @patch('twitterbot.twitter_client.requests.get')
    def test_get_requested_token(self, get):
        self.client._app_oauth1 = 'auth'
        self.client.requested_token = {'oauth_token': 'token_abc'}
        token = self.client.get_requested_token()
        expect(token).to.eq({
            'oauth_token': 'token_abc'
        })
        get.assert_not_called()

        self.client.requested_token = None
        get.return_value = Mock(content='key=value&token=abc')
        token = self.client.get_requested_token()
        get.assert_called_once_with(
            url='https://api.twitter.com/oauth/request_token',
            auth='auth'
        )
        expect(token).to.eq({
            'key': 'value',
            'token': 'abc'
        })

    def test_get_auth_url(self):
        self.client.requested_token = {'oauth_token': 'token_abc'}
        url = self.client.get_auth_url()
        expect(url).to.eq('https://api.twitter.com/oauth/authorize?oauth_token=token_abc&force_login=true')

    @patch('twitterbot.twitter_client.OAuth1')
    @patch('twitterbot.twitter_client.requests.post')
    def test_get_user_access_token(self, post, OAuth1):
        self.client.requested_token = {
            'oauth_token': 'token_abc',
            'oauth_token_secret': 'token_abc_secret'
        }
        OAuth1.return_value = 'auth'
        post.return_value = Mock(content='oauth_token=123&oauth_token_secret=456')

        access_token = self.client.get_user_access_token('123')

        OAuth1.assert_called_once_with(
            'consumer_key',
            client_secret='consumer_secret',
            resource_owner_key='token_abc',
            resource_owner_secret='token_abc_secret'
        )
        post.assert_called_once_with(
            url='https://api.twitter.com/oauth/access_token?oauth_verifier=123',
            auth='auth'
        )
        expect(access_token).to.eq({
            'account_token': '123',
            'account_token_secret': '456'
        })
