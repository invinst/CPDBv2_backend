from StringIO import StringIO

from django.test import SimpleTestCase
from django.core.management import call_command

from requests.exceptions import HTTPError
from mock import patch, MagicMock
from robber import expect


class CommandTestCase(SimpleTestCase):
    @patch('twitterbot.twitter_base_command.TwitterClient')
    def test_add_owner_subscription_success(self, TwitterClient):
        twitter_client_mock = TwitterClient()
        twitter_client_mock.subscription.return_value = MagicMock(add=MagicMock(return_value=[]))
        stdout, stderr = StringIO(), StringIO()

        call_command('add_owner_subscription', env='dev', stdout=stdout, stderr=stderr)

        twitter_client_mock.subscription.assert_called_once_with('dev')
        expect(stdout.getvalue().strip()).to.contain('Added app owner subscription successfully!')

    @patch('twitterbot.twitter_base_command.TwitterClient')
    def test_add_owner_subscription_fail(self, TwitterClient):
        twitter_client_mock = TwitterClient()
        exception = HTTPError(response=MagicMock(json=MagicMock(return_value=[])))
        add_mock = MagicMock()
        add_mock.side_effect = exception
        twitter_client_mock.subscription.return_value = MagicMock(add=add_mock)
        stdout, stderr = StringIO(), StringIO()

        call_command('add_owner_subscription', env='dev', stdout=stdout, stderr=stderr)

        twitter_client_mock.subscription.assert_called_once_with('dev')
        expect(stderr.getvalue().strip()).to.contain('Adding app owner subscription was not successful')
