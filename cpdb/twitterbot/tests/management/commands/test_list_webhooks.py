from StringIO import StringIO

from django.test import SimpleTestCase
from django.core.management import call_command

from mock import patch, Mock
from robber import expect


class CommandTestCase(SimpleTestCase):
    @patch('twitterbot.twitter_base_command.TwitterClient')
    def test_list_webhook(self, TwitterClient):
        twitter_client_mock = TwitterClient()
        twitter_client_mock.webhook.return_value = Mock(all=Mock(return_value=[]))
        stdout = StringIO()

        call_command('list_webhooks', env='dev', stdout=stdout)

        twitter_client_mock.webhook.assert_called_once_with('dev')
        expect(stdout.getvalue().strip()).to.eq('[]')
