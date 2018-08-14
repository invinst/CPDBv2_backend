from django.test import SimpleTestCase

from mock import Mock

from twitterbot.workers import ActivityEventWorker


class WorkerTestCase(SimpleTestCase):
    def test_process(self):
        event_worker = ActivityEventWorker()
        tweet_handler_mock = Mock()
        follow_handler_mock = Mock()
        event_worker.workers = {
            'tweet': tweet_handler_mock,
            'follow': follow_handler_mock
        }

        event_worker.process({
            'for_user_id': 123,
            'tweet': ['abc']
        })

        tweet_handler_mock().handle.assert_called()
        follow_handler_mock().handle.assert_not_called()
