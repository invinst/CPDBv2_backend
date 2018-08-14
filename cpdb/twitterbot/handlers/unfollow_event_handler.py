import logging

from twitterbot.tweets import TweetContext
from .base import SubEventHandler

logger = logging.getLogger(__name__)


class UnfollowEventHandler(SubEventHandler):
    def __init__(self, event_data, for_user_id, *args, **kwargs):
        super(UnfollowEventHandler, self).__init__(event_data, for_user_id, *args, **kwargs)
        self._context = {
            'client': self.client,
            'for_user_id': self.for_user_id
        }

        self.incoming_tweet = TweetContext(self.event_data, self._context)

    def match_tweet(self):
        return self.incoming_tweet.is_unfollow_tweet

    def handle(self):
        logger.info('%s - unfollow %s %s' % (
            self.__class__.__name__, self.incoming_tweet.screen_name, self.incoming_tweet.url))
        self.client.unfollow(self.incoming_tweet.user_id)
