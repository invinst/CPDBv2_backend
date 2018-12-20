import logging

from .base import EventHandler
from .officer_tweet_handler import OfficerTweetHandler
from .unfollow_event_handler import UnfollowEventHandler

logger = logging.getLogger(__name__)


class MentionEventHandler(EventHandler):
    sub_handlers = (OfficerTweetHandler, UnfollowEventHandler)

    def handle(self):
        for handler_cls in list(self.sub_handlers):
            handler = handler_cls(self.event_data, self.for_user_id, self.original_event)
            if handler.match_tweet():
                handler.handle()


class FollowEventHandler(EventHandler):
    def handle(self):
        from_user = self.event_data.get('source')
        if from_user.get('id') != str(self.client.get_current_user().id):
            logger.info(f"{self.__class__.__name__} - unfollow {from_user.get('screen_name')}")

            self.client.follow(from_user.get('id'))
