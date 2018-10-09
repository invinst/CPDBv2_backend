from django.test import SimpleTestCase

from mock import Mock

from twitterbot.handlers import MentionEventHandler, FollowEventHandler


class MentionEventHandlerTestCase(SimpleTestCase):
    def test_handle(self):
        handler = MentionEventHandler(event_data=None, for_user_id=123, original_event=None)
        match_sub_handler_mock = Mock()
        match_sub_handler_mock().match_tweet.return_value = True

        not_match_sub_handler_mock = Mock()
        not_match_sub_handler_mock().match_tweet.return_value = False

        handler.sub_handlers = (match_sub_handler_mock, not_match_sub_handler_mock)

        handler.handle()
        match_sub_handler_mock().handle.assert_called()
        not_match_sub_handler_mock().handle.assert_not_called()


class FollowEventHandlerTestCase(SimpleTestCase):
    def test_handle(self):
        handler = FollowEventHandler(event_data={'source': {'id': 456}}, for_user_id=123, original_event=None)
        handler.client = Mock(get_current_user=Mock(return_value=Mock(id=456)))

        handler.handle()

        handler.client.follow.assert_called()
