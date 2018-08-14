from django.conf import settings

import requests

from .constants import TWITTER_ACTIVITY_API


class WebhookManager(object):
    def __init__(self, oauth):
        self.oauth = oauth
        self.endpoint = TWITTER_ACTIVITY_API + '%s/webhooks.json'
        self.single_endpoint = TWITTER_ACTIVITY_API + '%s/webhooks/%s.json'
        self.environment_name = settings.TWITTERBOT_ENV

    def all(self):
        response = requests.get(
            url=self.endpoint % self.environment_name, auth=self.oauth
        )

        response.raise_for_status()
        return response.json()

    def register(self, webhook_url):
        response = requests.post(
            url=self.endpoint % self.environment_name,
            params={'url': webhook_url},
            auth=self.oauth
        )

        response.raise_for_status()
        return response.json()

    def remove(self, webhook_id):
        response = requests.delete(
            url=self.single_endpoint % (self.environment_name, webhook_id),
            auth=self.oauth
        )

        response.raise_for_status()
