import json

from twitterbot.twitter_base_command import TwitterBaseCommand


class Command(TwitterBaseCommand):
    def handle(self, *args, **options):
        token = self.twitter_client.get_bearer_token()

        if token:
            subscriptions = self.twitter_client.subscription.all(token)
            self.stdout.write(json.dumps(subscriptions, indent=2))
        else:
            self.stderr.write('Cannot get authentication token')
