from django.test import SimpleTestCase

from mock import Mock
from robber import expect
from tweepy import TweepError

from twitterbot.wrappers import (
    TweepyWrapper, TWITTER_USER_NOT_FOUND_ERROR,
    TWITTER_ACCOUNT_SUSPENDED_ERROR, TWITTER_TWEET_NOT_FOUND_ERROR
)


class TweepyWrapperTestCase(SimpleTestCase):
    def test_tweepy_api(self):
        wrapper = TweepyWrapper(client='abc')
        expect(wrapper.tweepy_api).to.eq('abc')

    def test_get_current_user(self):
        wrapper = TweepyWrapper(client=Mock(me=Mock(return_value=Mock(_json={'abc': 123}))))
        expect(wrapper.get_current_user().raw_data).to.eq({'abc': 123})

        wrapper = TweepyWrapper(client=None)
        wrapper._current_user = 'abc'
        expect(wrapper.get_current_user()).to.eq('abc')

    def test_get_user(self):
        wrapper = TweepyWrapper(client=Mock(get_user=Mock(return_value=Mock(_json={'abc': 123}))))
        expect(wrapper.get_user(1).raw_data).to.eq({'abc': 123})
        expect(wrapper._user_dict[1].raw_data).to.eq({'abc': 123})

        wrapper = TweepyWrapper(client=None)
        wrapper._user_dict = {1: 'abc'}
        expect(wrapper.get_user(1)).to.eq('abc')

        get_user_mock = Mock()
        get_user_mock.side_effect = TweepError(None, api_code=TWITTER_USER_NOT_FOUND_ERROR)
        wrapper = TweepyWrapper(client=Mock(get_user=get_user_mock))
        expect(wrapper.get_user(1)).to.be.none()

        get_user_mock.side_effect = TweepError(None, api_code=11111)
        wrapper = TweepyWrapper(client=Mock(get_user=get_user_mock))
        expect(lambda: wrapper.get_user(1)).to.throw(TweepError)

    def test_unfollow(self):
        wrapper = TweepyWrapper(client=Mock(destroy_friendship=Mock(return_value=Mock(_json={'abc': 123}))))
        expect(wrapper.unfollow(1).raw_data).to.eq({'abc': 123})

    def test_follow(self):
        wrapper = TweepyWrapper(client=Mock(create_friendship=Mock(return_value=Mock(_json={'abc': 123}))))
        expect(wrapper.follow(1).raw_data).to.eq({'abc': 123})

        create_friendship_mock = Mock()
        create_friendship_mock.side_effect = TweepError(None, api_code=TWITTER_ACCOUNT_SUSPENDED_ERROR)
        client_mock = Mock(
            create_friendship=create_friendship_mock,
            get_user=Mock(return_value=Mock(_json={'abc': 456}))
        )
        wrapper = TweepyWrapper(client=client_mock)
        expect(wrapper.follow(1).raw_data).to.eq({'abc': 456})

        create_friendship_mock = Mock()
        create_friendship_mock.side_effect = TweepError(None, api_code=1111)
        wrapper = TweepyWrapper(client=Mock(create_friendship=create_friendship_mock))
        expect(lambda: wrapper.follow(1)).to.throw(TweepError)

    def test_get_tweet(self):
        wrapper = TweepyWrapper(client=Mock(get_status=Mock(return_value=Mock(_json={'abc': 123}))))
        expect(wrapper.get_tweet(1).raw_data).to.eq({'abc': 123})

        get_status_mock = Mock()
        get_status_mock.side_effect = TweepError(None, api_code=TWITTER_TWEET_NOT_FOUND_ERROR)
        client_mock = Mock(
            get_status=get_status_mock,
            get_user=Mock(return_value=Mock(_json={'abc': 456}))
        )
        wrapper = TweepyWrapper(client=client_mock)
        expect(wrapper.get_tweet(1)).to.be.none()

        get_status_mock = Mock()
        get_status_mock.side_effect = TweepError(None, api_code=1111)
        wrapper = TweepyWrapper(client=Mock(get_status=get_status_mock))
        expect(lambda: wrapper.get_tweet(1)).to.throw(TweepError)
