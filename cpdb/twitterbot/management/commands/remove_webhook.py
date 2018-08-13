import json

from requests.exceptions import HTTPError

from twitterbot.twitter_base_command import TwitterBaseCommand


class Command(TwitterBaseCommand):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--id',
            dest='id',
            help='webhook id'
        )

    def handle(self, *args, **options):
        id = options['id']

        try:
            self.twitter_client.webhook(self.environment).remove(id)
            self.stdout.write('Remove webhook successfully!')
        except HTTPError as e:
            self.stderr.write('Removing wehook was not successful')
            self.stderr.write(json.dumps(e.response.json(), indent=2))
