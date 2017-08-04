from django.conf import settings
from django.core.management.base import BaseCommand

from responsebot.responsebot import ResponseBot


class Command(BaseCommand):
    def handle(self, *args, **options):
        options['auth'] = (
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET,
            settings.TWITTER_APP_TOKEN_KEY,
            settings.TWITTER_APP_TOKEN_SECRET
        )
        options['handlers_package'] = 'twitterbot.handlers'
        options['user_stream'] = True

        bot = ResponseBot(*args, **options)
        bot.start()
