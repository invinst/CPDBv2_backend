from django.conf import settings

import requests
from requests_oauthlib import OAuth1

from .constants import TWITTER_ACTIVITY_API


class SubscriptionsManager(object):
    def __init__(self, consumer_key, consumer_secret, *arg, **kwargs):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        environment_name = settings.TWITTERBOT_ENV
        self.list_endpoint = f'{TWITTER_ACTIVITY_API}{environment_name}/subscriptions/list.json'
        self.endpoint = f'{TWITTER_ACTIVITY_API}{environment_name}/subscriptions.json'

    def get_account_oauth(self, account_token, account_token_secret):
        return OAuth1(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=account_token,
            resource_owner_secret=account_token_secret
        )

    def all(self, app_bearer_token):
        response = requests.get(
            url=self.list_endpoint,
            headers={'Authorization': f'Bearer {app_bearer_token}'}
        )
        response.raise_for_status()
        return response.json()

    def add(self, account_token, account_token_secret):
        account_oauth = self.get_account_oauth(account_token, account_token_secret)
        response = requests.post(url=self.endpoint, auth=account_oauth)
        response.raise_for_status()

    def remove(self, account_token, account_token_secret):
        account_oauth = self.get_account_oauth(account_token, account_token_secret)
        response = requests.delete(url=self.endpoint, auth=account_oauth)
        response.raise_for_status()
