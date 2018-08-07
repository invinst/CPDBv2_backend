from django.core.management.base import BaseCommand
from django.conf import settings

from twitterbot.twitter_client import TwitterClient


class TwitterBaseCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(TwitterBaseCommand, self).__init__(*args, **kwargs)
        self.twitter_client = TwitterClient(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            app_token_key=settings.TWITTER_APP_TOKEN_KEY,
            app_token_secret=settings.TWITTER_APP_TOKEN_SECRET
        )

    def add_arguments(self, parser):
        parser.add_argument(
            '--env',
            dest='env',
            help='Specify the environment'
        )
