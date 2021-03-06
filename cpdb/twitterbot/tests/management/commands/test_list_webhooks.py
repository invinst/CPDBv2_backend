from io import StringIO

from django.test import SimpleTestCase
from django.core.management import call_command

from mock import patch, Mock
from robber import expect


class CommandTestCase(SimpleTestCase):
    @patch('twitterbot.twitter_base_command.TwitterClient')
    def test_list_webhook(self, TwitterClient):
        twitter_client_mock = TwitterClient()
        twitter_client_mock.webhook = Mock(all=Mock(return_value=[]))
        stdout = StringIO()

        call_command('list_webhooks', stdout=stdout)

        expect(stdout.getvalue().strip()).to.eq('[]')
