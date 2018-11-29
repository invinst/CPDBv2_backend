from io import StringIO

from django.test import SimpleTestCase
from django.core.management import call_command

from requests.exceptions import HTTPError
from mock import patch, MagicMock
from robber import expect


class CommandTestCase(SimpleTestCase):
    @patch('twitterbot.twitter_base_command.TwitterClient')
    def test_register_webhook_success(self, TwitterClient):
        twitter_client_mock = TwitterClient()
        twitter_client_mock.webhook = MagicMock(register=MagicMock(return_value=[]))
        stdout, stderr = StringIO(), StringIO()

        call_command('register_webhook', url='http://webhook.api', stdout=stdout, stderr=stderr)

        expect(stdout.getvalue().strip()).to.contain('Webhook was registered successfully')

    @patch('twitterbot.twitter_base_command.TwitterClient')
    def test_register_webhook_fail(self, TwitterClient):
        twitter_client_mock = TwitterClient()
        exception = HTTPError(response=MagicMock(json=MagicMock(return_value=[])))
        register_mock = MagicMock()
        register_mock.side_effect = exception
        twitter_client_mock.webhook = MagicMock(register=register_mock)
        stdout, stderr = StringIO(), StringIO()

        call_command('register_webhook', url='http://webhook.api', stdout=stdout, stderr=stderr)

        expect(stderr.getvalue().strip()).to.contain('Registering wehook was not successful')
