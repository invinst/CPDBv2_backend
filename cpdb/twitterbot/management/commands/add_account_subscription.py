import json

from requests.exceptions import HTTPError

from twitterbot.twitter_base_command import TwitterBaseCommand
from twitterbot.utils.user_input import get_user_input


class Command(TwitterBaseCommand):
    def handle(self, *args, **options):
        environment = options['env']

        try:
            auth_url = self.twitter_client.get_auth_url()
            self.stdout.write(
                'Open this URL in a browser and sign-in with the Twitter account you wish to subscribe to:'
            )
            self.stdout.write(auth_url)
            pin = get_user_input('Enter the generated PIN:')

            if pin:
                user_access_token = self.twitter_client.get_user_access_token(pin)
                self.twitter_client.subscription(environment).add(
                    user_access_token['account_token'], user_access_token['account_token_secret']
                )
                self.stdout.write('Added user subscription successfully!')
            else:
                self.stderr.write('Failed to get user authorization.')
        except HTTPError as e:
            self.stderr.write('Adding user subscription was not successful')
            self.stderr.write(json.dumps(e.response.content, indent=2))
