import json

from twitterbot.twitter_base_command import TwitterBaseCommand


class Command(TwitterBaseCommand):
    def handle(self, *args, **options):
        webhooks = self.twitter_client.webhook.all()
        self.stdout.write(json.dumps(webhooks, indent=2))
