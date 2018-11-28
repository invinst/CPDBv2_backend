from urllib.parse import parse_qs

import requests
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth2Session

from .webhook_manager import WebhookManager
from .subscription_manager import SubscriptionsManager


class TwitterClient(object):
    requested_token = None

    def __init__(self, consumer_key, consumer_secret, app_token_key, app_token_secret, *args, **kwargs):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.app_token_key = app_token_key
        self.app_token_secret = app_token_secret

        self._app_oauth1 = OAuth1(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=app_token_key,
            resource_owner_secret=app_token_secret
        )
        self._webhook = WebhookManager(self._app_oauth1)
        self._subscription = SubscriptionsManager(consumer_key, consumer_secret)

    @property
    def webhook(self):
        return self._webhook

    @property
    def subscription(self):
        return self._subscription

    def get_bearer_token(self):
        auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        oauth = OAuth2Session(client=BackendApplicationClient(self.consumer_key))
        token = oauth.fetch_token(
            token_url='https://api.twitter.com/oauth2/token',
            auth=auth
        )

        return token.get('access_token')

    def get_requested_token(self):
        if self.requested_token is not None:
            return self.requested_token

        response = requests.get(
            url='https://api.twitter.com/oauth/request_token',
            auth=self._app_oauth1
        )
        response.raise_for_status()
        self.requested_token = {
            key: value[0]
            for key, value in parse_qs(response.content).items()
        }

        return self.requested_token

    def get_auth_url(self):
        requested_token = self.get_requested_token()

        return (
            'https://api.twitter.com/oauth/authorize?oauth_token=%s&force_login=true'
            % requested_token['oauth_token']
        )

    def get_user_access_token(self, pin):
        requested_token = self.get_requested_token()

        account_auth = OAuth1(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=requested_token['oauth_token'],
            resource_owner_secret=requested_token['oauth_token_secret']
        )

        response = requests.post(
            url='https://api.twitter.com/oauth/access_token?oauth_verifier=%s' % pin,
            auth=account_auth
        )
        response.raise_for_status()
        token_response = parse_qs(response.content)

        return {
            'account_token': token_response['oauth_token'][0],
            'account_token_secret': token_response['oauth_token_secret'][0]
        }
