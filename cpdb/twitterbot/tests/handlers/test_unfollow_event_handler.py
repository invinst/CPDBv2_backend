from django.test import SimpleTestCase

from mock import Mock, patch
from robber import expect

from twitterbot.handlers.unfollow_event_handler import UnfollowEventHandler


class UnfollowEventHandlerTestCase(SimpleTestCase):
    @patch('twitterbot.handlers.unfollow_event_handler.TweetContext')
    def test_match_tweet(self, tweet_context):
        tweet_context_mock = tweet_context()
        tweet_context_mock.is_unfollow_tweet = True

        handler = UnfollowEventHandler(event_data=None, for_user_id=123)
        expect(handler.match_tweet()).to.be.true()

        tweet_context_mock.is_unfollow_tweet = False
        expect(handler.match_tweet()).to.be.false()

    @patch('twitterbot.handlers.unfollow_event_handler.TweetContext')
    def test_handle(self, tweet_context):
        unfollow_mock = Mock()
        with patch('twitterbot.handlers.base.TweepyWrapper', return_value=Mock(unfollow=unfollow_mock)):
            handler = UnfollowEventHandler(event_data=None, for_user_id=123)
            tweet_context_mock = tweet_context()
            tweet_context_mock.user_id = 123

            handler.handle()
            unfollow_mock.assert_called_with(123)
