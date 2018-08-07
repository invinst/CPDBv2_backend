from StringIO import StringIO

from django.test import SimpleTestCase
from django.core.management import call_command

from mock import patch, Mock
from robber import expect


class CommandTestCase(SimpleTestCase):
    @patch('twitterbot.twitter_base_command.TwitterClient')
    def test_list_subscriptions(self, TwitterClient):
        twitter_client_mock = TwitterClient()
        twitter_client_mock.get_bearer_token.return_value = '123'
        twitter_client_mock.subscription.return_value = Mock(all=Mock(return_value=[]))
        stdout = StringIO()

        call_command('list_subscriptions', env='dev', stdout=stdout)

        twitter_client_mock.subscription.assert_called_once_with('dev')
        expect(stdout.getvalue().strip()).to.eq('[]')

    @patch('twitterbot.twitter_base_command.TwitterClient')
    def test_list_subscriptions_fail(self, TwitterClient):
        twitter_client_mock = TwitterClient()
        twitter_client_mock.get_bearer_token.return_value = None
        twitter_client_mock.subscription.return_value = Mock(all=Mock(return_value=[]))
        stderr = StringIO()

        call_command('list_subscriptions', env='dev', stderr=stderr)

        twitter_client_mock.subscription.assert_not_called()
        expect(stderr.getvalue().strip()).to.contain('Cannot get authentication token')
