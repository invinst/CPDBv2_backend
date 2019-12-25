import requests
import json

from twitterbot.twitter_base_command import TwitterBaseCommand
from django.conf import settings

VALID_WEBHOOK_COLOR = '#028090'
INVALID_WEBHOOK_COLOR = '#F9001E'


class Command(TwitterBaseCommand):
    def handle(self, *args, **options):
        webhooks = self.twitter_client.webhook.all()

        if webhooks:
            valid = all([webhook['valid'] for webhook in webhooks])
            webhook_statuses = [
                {
                    'color': VALID_WEBHOOK_COLOR if webhook["valid"] else INVALID_WEBHOOK_COLOR,
                    'title': f'{webhook["url"]} is {"valid" if webhook["valid"] else "invalid"}'
                }
                for webhook in webhooks
            ]
            requests.post(
                settings.CPDP_ALERTS_WEBHOOK,
                headers={'Content-type': 'application/json'},
                data=json.dumps({
                    'text': f'{"<!channel> " if not valid else ""}Twitter webhook is {"valid" if valid else "invalid"}'
                            f' for {settings.TWITTERBOT_ENV}',
                    'attachments': webhook_statuses
                })
            )
