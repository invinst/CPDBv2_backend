import json

from requests.exceptions import HTTPError

from twitterbot.twitter_base_command import TwitterBaseCommand


class Command(TwitterBaseCommand):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--url',
            dest='url',
            help='webhook url'
        )

    def handle(self, *args, **options):
        environment = options['env']
        url = options['url']

        try:
            webhook = self.twitter_client.webhook(environment).register(url)
            self.stdout.write(json.dumps(webhook, indent=2))
            self.stdout.write('Webhook was registered successfully')
        except HTTPError as e:
            self.stderr.write('Registering wehook was not successful')
            self.stderr.write(json.dumps(e.response.json(), indent=2))
