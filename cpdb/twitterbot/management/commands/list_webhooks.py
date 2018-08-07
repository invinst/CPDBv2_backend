import json

from twitterbot.twitter_base_command import TwitterBaseCommand


class Command(TwitterBaseCommand):
    def handle(self, *args, **options):
        environment = options['env']
        webhooks = self.twitter_client.webhook(environment).all()
        self.stdout.write(json.dumps(webhooks, indent=2))
