import json

from django.conf import settings

from requests.exceptions import HTTPError

from twitterbot.twitter_base_command import TwitterBaseCommand


class Command(TwitterBaseCommand):
    def handle(self, *args, **options):
        environment = options['env']

        try:
            self.twitter_client.subscription(environment).add(
                settings.TWITTER_APP_TOKEN_KEY, settings.TWITTER_APP_TOKEN_SECRET
            )
            self.stdout.write('Added app owner subscription successfully!')
        except HTTPError as e:
            self.stderr.write('Adding app owner subscription was not successful')
            self.stderr.write(json.dumps(e.response.json(), indent=2))
