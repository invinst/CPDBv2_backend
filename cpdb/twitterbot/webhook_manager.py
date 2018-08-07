import requests


class WebhookManager(object):
    def __init__(self, oauth):
        self.oauth = oauth
        self.endpoint = 'https://api.twitter.com/1.1/account_activity/all/%s/webhooks.json'
        self.single_endpoint = 'https://api.twitter.com/1.1/account_activity/all/%s/webhooks/%s.json'

    def set_environment_name(self, environment_name):
        self.environment_name = environment_name

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
