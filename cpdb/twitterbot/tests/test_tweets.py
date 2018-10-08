from datetime import datetime

from django.test import SimpleTestCase

import pytz
from robber import expect

from twitterbot.tweets import TweetContext
from twitterbot.factories import TweetFactory, MockTweepyWrapperFactory


class TweetTestCase(SimpleTestCase):
    def setUp(self):
        super(TweetTestCase, self).setUp()
        self.original_tweet = {
            'text': 'some content',
            'entities': {
                'urls': [{'expanded_url': 'http://abc.com'}],
                'hashtags': [{'text': 'def'}],
                'user_mentions': [{'screen_name': 'Abc'}]
            }
        }
        self.client = MockTweepyWrapperFactory()
        self.context = {
            'client': self.client,
            'for_user_id': 123
        }

    def test_text_property(self):
        tweet = TweetContext(original_tweet=self.original_tweet)
        expect(tweet.text).to.eq('some content')

    def test_urls_property(self):
        tweet = TweetContext(original_tweet=self.original_tweet, context=self.context)
        expect(tweet.urls).to.eq(['http://abc.com'])

    def test_empty_urls(self):
        tweet = TweetContext(original_tweet={'text': '', 'entities': {}}, context=self.context)
        expect(tweet.urls).to.eq([])

    def test_urls_not_including_self_tweet_url(self):
        original_tweet = {
            'entities': {
                'urls': [{'expanded_url': 'http://twitter.com/Abc'}]
            }
        }
        tweet = TweetContext(
            original_tweet=original_tweet,
            context={
                'client': MockTweepyWrapperFactory(subscription_screen_name='Abc'),
                'for_user_id': 123
            }
        )
        expect(tweet.urls).to.eq([])

    def test_hashtags_property(self):
        tweet = TweetContext(original_tweet=self.original_tweet)
        expect(tweet.hashtags).to.eq(['def'])

    def test_empty_hashtags(self):
        tweet = TweetContext({
            'text': '',
            'entities': {}
        })
        expect(tweet.hashtags).to.eq([])

    def test_tweet_user_id(self):
        original_tweet = {'user': {'id': 123}}
        tweet = TweetContext(original_tweet=original_tweet, context=self.context)
        expect(tweet.user_id).to.eq(123)

    def test_tweet_screen_name(self):
        original_tweet = {'user': {'screen_name': 'Abc'}}
        tweet = TweetContext(original_tweet=original_tweet)
        expect(tweet.screen_name).to.equal('Abc')

    def test_user_mention_screen_names(self):
        tweet = TweetFactory(original_tweet=self.original_tweet)
        expect(tweet.user_mention_screen_names).to.eq(['Abc'])

    def test_in_reply_to_tweet(self):
        in_reply_to_tweet = TweetFactory(id=123)
        client = MockTweepyWrapperFactory()
        client.register(in_reply_to_tweet)
        tweet = TweetContext(original_tweet={'in_reply_to_tweet_id': 123}, context={'client': client})
        expect(tweet.in_reply_to_tweet.id).to.eq(123)
        expect(tweet.in_reply_to_tweet).to.eq(tweet.in_reply_to_tweet)

    def test_retweeted_status(self):
        client = MockTweepyWrapperFactory()
        retweeted_status = TweetFactory(id=123)
        client.register(retweeted_status)
        tweet = TweetContext(original_tweet={'retweeted_status': {'id': 123}}, context={'client': client})
        expect(tweet.retweeted_status.id).to.eq(123)
        expect(tweet.retweeted_status).to.eq(tweet.retweeted_status)

    def test_quoted_tweet(self):
        client = MockTweepyWrapperFactory()
        quoted_tweet = TweetFactory(id=123)
        client.register(quoted_tweet)
        tweet = TweetContext(original_tweet={'quoted_tweet': {'id': 123}}, context={'client': client})
        expect(tweet.quoted_tweet.id).to.eq(123)
        expect(tweet.quoted_tweet).to.eq(tweet.quoted_tweet)

    def test_quoted_tweet_id(self):
        client = MockTweepyWrapperFactory()
        quoted_tweet = TweetFactory(id=123)
        client.register(quoted_tweet)
        tweet = TweetContext(original_tweet={'quoted_tweet_id': 123, 'quoted_tweet': None}, context={'client': client})
        expect(tweet.quoted_tweet.id).to.eq(123)

    def test_is_retweet(self):
        expect(TweetContext(original_tweet={'retweeted_status': None}).is_retweet).to.be.false()
        expect(TweetContext(original_tweet={'retweeted_status': {}}).is_retweet).to.be.true()

    def test_tweet_url(self):
        tweet = TweetContext(original_tweet={'id': 123, 'user': {'screen_name': 'abc'}})
        expect(tweet.url).to.eq('https://twitter.com/abc/status/123/')

    def test_tweet_created_at(self):
        created_at = datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc)
        tweet = TweetContext(original_tweet={'created_at': '2017-08-04T14:30:00Z'})
        expect(tweet.created_at).to.eq(created_at)

    def test_is_retweet_of_twitterbot(self):
        original_tweet = {'retweeted_status': {'user': {'id': 456}}}
        client = MockTweepyWrapperFactory()
        tweet = TweetContext(original_tweet=original_tweet, context={'client': client, 'for_user_id': 456})
        expect(tweet.is_retweet_of_twitterbot).to.be.true()

        tweet = TweetContext(original_tweet=original_tweet, context={'client': client, 'for_user_id': 123})
        expect(tweet.is_retweet_of_twitterbot).to.be.false()

    def test_is_quoted_tweet_of_twitterbot(self):
        original_tweet = {'quoted_tweet': {'user': {'id': 123}}}
        client = MockTweepyWrapperFactory()
        tweet = TweetContext(original_tweet=original_tweet, context={'client': client, 'for_user_id': 123})
        expect(tweet.is_quoted_tweet_of_twitterbot).to.be.true()

        tweet = TweetContext(original_tweet=original_tweet, context={'client': client, 'for_user_id': 456})
        expect(tweet.is_quoted_tweet_of_twitterbot).to.be.false()

    def test_is_tweet_from_followed_accounts(self):
        client = MockTweepyWrapperFactory(followed_by=True)
        tweet = TweetContext(original_tweet={}, context={'client': client, 'for_user_id': 123})
        expect(tweet.is_tweet_from_followed_accounts).to.be.true()

        client = MockTweepyWrapperFactory(followed_by=False)
        tweet = TweetContext(original_tweet={}, context={'client': client, 'for_user_id': 123})
        expect(tweet.is_tweet_from_followed_accounts).to.be.false()

    def test_is_unfollow_tweet(self):
        client = MockTweepyWrapperFactory(subscription_screen_name='abc')
        tweet = TweetContext(original_tweet={'text': '@abc STOP'}, context={'client': client, 'for_user_id': 123})
        expect(tweet.is_unfollow_tweet).to.be.true()

        tweet = TweetContext(original_tweet={'text': 'anything else'}, context={'client': client, 'for_user_id': 123})
        expect(tweet.is_unfollow_tweet).to.be.false()

    def test_is_mentioning_twitterbot(self):
        client = MockTweepyWrapperFactory(screen_name='abc')
        context = {
            'client': client,
            'for_user_id': 123
        }
        tweet = TweetFactory(text='something', user_mentions=[{'id': 123}], context=context)
        expect(tweet.is_mentioning_twitterbot).to.be.true()

        tweet = TweetFactory(text='something', context=context)
        expect(tweet.is_mentioning_twitterbot).to.be.false()
