from django.test import SimpleTestCase

from mock import Mock

from twitterbot.events_hub import ActivityEventHub


class WorkerTestCase(SimpleTestCase):
    def test_process(self):
        events_hub = ActivityEventHub()
        tweet_handler_mock = Mock()
        follow_handler_mock = Mock()
        events_hub.event_handlers = {
            'tweet': tweet_handler_mock,
            'follow': follow_handler_mock
        }

        events_hub.handle_event({
            'for_user_id': 123,
            'tweet': ['abc']
        })

        tweet_handler_mock().handle.assert_called()
        follow_handler_mock().handle.assert_not_called()
