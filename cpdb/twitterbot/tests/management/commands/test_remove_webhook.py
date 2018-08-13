from StringIO import StringIO

from django.test import SimpleTestCase
from django.core.management import call_command

from requests.exceptions import HTTPError
from mock import patch, MagicMock
from robber import expect


class CommandTestCase(SimpleTestCase):
    @patch('twitterbot.twitter_base_command.TwitterClient')
    def test_remove_webhook_success(self, TwitterClient):
        twitter_client_mock = TwitterClient()
        twitter_client_mock.webhook.return_value = MagicMock(remove=MagicMock(return_value=[]))
        stdout, stderr = StringIO(), StringIO()

        call_command('remove_webhook', id=123, stdout=stdout, stderr=stderr)

        twitter_client_mock.webhook.assert_called_once_with('test')
        expect(stdout.getvalue().strip()).to.contain('Remove webhook successfully!')

    @patch('twitterbot.twitter_base_command.TwitterClient')
    def test_remove_webhook_fail(self, TwitterClient):
        twitter_client_mock = TwitterClient()
        exception = HTTPError(response=MagicMock(json=MagicMock(return_value=[])))
        register_mock = MagicMock()
        register_mock.side_effect = exception
        twitter_client_mock.webhook.return_value = MagicMock(remove=register_mock)
        stdout, stderr = StringIO(), StringIO()

        call_command('remove_webhook', id=123, stdout=stdout, stderr=stderr)

        twitter_client_mock.webhook.assert_called_once_with('test')
        expect(stderr.getvalue().strip()).to.contain('Removing wehook was not successful')
