from StringIO import StringIO

from django.test import SimpleTestCase
from django.core.management import call_command

from mock import patch, Mock
from robber import expect
from requests.exceptions import HTTPError


class CommandTestCase(SimpleTestCase):
    @patch('twitterbot.twitter_base_command.TwitterClient')
    @patch('twitterbot.management.commands.add_account_subscription.get_user_input', return_value=None)
    def test_add_account_subscription_no_pin(self, get_user_input, TwitterClient):
        twitter_client_mock = TwitterClient()
        twitter_client_mock.get_auth_url.return_value = 'auth_url'
        twitter_client_mock.subscription.return_value = Mock(all=Mock(return_value=[]))
        stdout, stderr = StringIO(), StringIO()

        call_command('add_account_subscription', env='dev', stdout=stdout, stderr=stderr)

        expect(stdout.getvalue().strip()).to.contain('auth_url')
        expect(stderr.getvalue().strip()).to.contain('Failed to get user authorization.')

    @patch('twitterbot.twitter_base_command.TwitterClient')
    @patch('twitterbot.management.commands.add_account_subscription.get_user_input', return_value='123')
    def test_add_account_subscription_fail(self, get_user_input, TwitterClient):
        twitter_client_mock = TwitterClient()
        exception = HTTPError(response=Mock(content=[]))
        twitter_client_mock.get_user_access_token.side_effect = exception
        stdout, stderr = StringIO(), StringIO()

        call_command('add_account_subscription', env='dev', stdout=stdout, stderr=stderr)

        expect(stderr.getvalue().strip()).to.contain('Adding user subscription was not successful')

    @patch('twitterbot.twitter_base_command.TwitterClient')
    @patch('twitterbot.management.commands.add_account_subscription.get_user_input', return_value='123')
    def test_add_account_subscription_success(self, get_user_input, TwitterClient):
        twitter_client_mock = TwitterClient()
        twitter_client_mock.subscription.return_value = Mock(add=Mock(return_value=[]))
        twitter_client_mock.get_user_access_token.return_value = {
            'account_token': 'token',
            'account_token_secret': 'token_secret'
        }
        stdout, stderr = StringIO(), StringIO()

        call_command('add_account_subscription', env='dev', stdout=stdout, stderr=stderr)

        expect(stdout.getvalue().strip()).to.contain('Added user subscription successfully!')
