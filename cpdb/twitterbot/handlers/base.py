from django.conf import settings

import tweepy

from twitterbot.wrappers import TweepyWrapper


class EventHandler(object):
    def __init__(self, event_data, for_user_id, *args, **kwargs):
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(settings.TWITTER_APP_TOKEN_KEY, settings.TWITTER_APP_TOKEN_SECRET)
        self.client = TweepyWrapper(tweepy.API(auth))
        self.event_data = event_data
        self.for_user_id = for_user_id

    def handle(self):  # pragma: no cover
        raise NotImplementedError


class SubEventHandler(EventHandler):
    def match_tweet(self):  # pragma: no cover
        raise NotImplementedError
