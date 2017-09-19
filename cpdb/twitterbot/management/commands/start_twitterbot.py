import newrelic.agent
from django.conf import settings

if not settings.TEST:
    newrelic.agent.initialize(str(settings.TWITTERBOT_NEW_RELIC_CONFIG_FILE_PATH))

from django.core.management.base import BaseCommand  # noqa E402

from responsebot.responsebot import ResponseBot  # noqa E402


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
