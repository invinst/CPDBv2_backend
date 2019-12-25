import json

from django.test import SimpleTestCase
from django.core.management import call_command
from django.conf import settings

from mock import patch, Mock
from robber import expect


class CommandTestCase(SimpleTestCase):
    @patch('twitterbot.twitter_base_command.TwitterClient')
    @patch('twitterbot.management.commands.webhook_statuses_check.requests')
    def test_webhook_statuses_check_valid(self, requests_mock, TwitterClientMock):
        twitter_client_mock = TwitterClientMock()
        webhooks = [{
            'id': 'webhook1',
            'url': 'https://webhook_url/',
            'valid': True,
            'created_timestamp': '2018-11-14 09:28:48 +0000'
        }]
        twitter_client_mock.webhook = Mock(all=Mock(return_value=webhooks))

        call_command('webhook_statuses_check')

        expect(requests_mock.post).to.be.called_once_with(
            settings.CPDP_ALERTS_WEBHOOK,
            headers={'Content-type': 'application/json'},
            data=json.dumps({
                'text': 'Twitter webhook is valid'
                        f' for {settings.TWITTERBOT_ENV}',
                'attachments': [{
                    'color': '#028090',
                    'title': 'https://webhook_url/ is valid'
                }]
            })
        )

    @patch('twitterbot.twitter_base_command.TwitterClient')
    @patch('twitterbot.management.commands.webhook_statuses_check.requests')
    def test_webhook_statuses_check_invalid(self, requests_mock, TwitterClientMock):
        twitter_client_mock = TwitterClientMock()
        webhooks = [{
            'id': 'webhook1',
            'url': 'https://webhook_url/',
            'valid': False,
            'created_timestamp': '2018-11-14 09:28:48 +0000'
        }]
        twitter_client_mock.webhook = Mock(all=Mock(return_value=webhooks))

        call_command('webhook_statuses_check')

        expect(requests_mock.post).to.be.called_once_with(
            settings.CPDP_ALERTS_WEBHOOK,
            headers={'Content-type': 'application/json'},
            data=json.dumps({
                'text': '<!channel> Twitter webhook is invalid'
                        f' for {settings.TWITTERBOT_ENV}',
                'attachments': [{
                    'color': '#F9001E',
                    'title': 'https://webhook_url/ is invalid'
                }]
            })
        )
