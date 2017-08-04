from datetime import datetime

from django.test import SimpleTestCase

from robber import expect
from mock import Mock

from twitterbot.tweets import Tweet
from twitterbot.factories import TweetFactory, MockClientFactory


class TweetTestCase(SimpleTestCase):
    def setUp(self):
        super(TweetTestCase, self).setUp()
        self.original_tweet = Mock(
            text='some content',
            entities={
                'urls': [{'expanded_url': 'http://abc.com'}],
                'hashtags': [{'text': 'def'}],
                'user_mentions': [{'screen_name': 'Abc'}]
            })
        self.client = MockClientFactory()

    def test_text_property(self):
        tweet = Tweet(original_tweet=self.original_tweet)
        expect(tweet.text).to.eq('some content')

    def test_urls_property(self):
        tweet = Tweet(original_tweet=self.original_tweet, client=self.client)
        expect(tweet.urls).to.eq(['http://abc.com'])

    def test_empty_urls(self):
        tweet = Tweet(original_tweet=Mock(text='', entities={}), client=self.client)
        expect(tweet.urls).to.eq([])

    def test_urls_not_including_self_tweet_url(self):
        original_tweet = Mock(
            entities={
                'urls': [{'expanded_url': 'http://twitter.com/Abc'}]
            })
        tweet = Tweet(
            original_tweet=original_tweet,
            client=Mock(get_current_user=Mock(return_value=Mock(screen_name='Abc')))
        )
        expect(tweet.urls).to.eq([])

    def test_hashtags_property(self):
        tweet = Tweet(original_tweet=self.original_tweet)
        expect(tweet.hashtags).to.eq(['def'])

    def test_empty_hashtags(self):
        tweet = Tweet(Mock(
            text='',
            entities={}))
        expect(tweet.hashtags).to.eq([])

    def test_tweet_user_id(self):
        original_tweet = Mock(user=Mock(id=123))
        tweet = Tweet(original_tweet=original_tweet, client=self.client)
        expect(tweet.user_id).to.eq(123)

    def test_tweet_screen_name(self):
        original_tweet = Mock(user=Mock(screen_name='Abc'))
        tweet = Tweet(original_tweet=original_tweet)
        expect(tweet.screen_name).to.equal('Abc')

    def test_user_mention_screen_names(self):
        tweet = TweetFactory(original_tweet=self.original_tweet)
        expect(tweet.user_mention_screen_names).to.eq(['Abc'])

    def test_in_reply_to_tweet(self):
        in_reply_to_tweet = TweetFactory(id=123)
        client = MockClientFactory()
        client.register(in_reply_to_tweet)
        tweet = Tweet(original_tweet=Mock(in_reply_to_tweet_id=123), client=client)
        expect(tweet.in_reply_to_tweet.id).to.eq(123)
        expect(tweet.in_reply_to_tweet).to.eq(tweet.in_reply_to_tweet)

    def test_retweeted_tweet(self):
        client = MockClientFactory()
        retweeted_tweet = TweetFactory(id=123)
        client.register(retweeted_tweet)
        tweet = Tweet(original_tweet=Mock(retweeted_tweet=Mock(id=123)), client=client)
        expect(tweet.retweeted_tweet.id).to.eq(123)
        expect(tweet.retweeted_tweet).to.eq(tweet.retweeted_tweet)

    def test_quoted_tweet(self):
        client = MockClientFactory()
        quoted_tweet = TweetFactory(id=123)
        client.register(quoted_tweet)
        tweet = Tweet(original_tweet=Mock(quoted_tweet=Mock(id=123)), client=client)
        expect(tweet.quoted_tweet.id).to.eq(123)
        expect(tweet.quoted_tweet).to.eq(tweet.quoted_tweet)

    def test_quoted_tweet_id(self):
        client = MockClientFactory()
        quoted_tweet = TweetFactory(id=123)
        client.register(quoted_tweet)
        tweet = Tweet(original_tweet=Mock(quoted_tweet_id=123, quoted_tweet=None), client=client)
        expect(tweet.quoted_tweet.id).to.eq(123)

    def test_is_retweet(self):
        expect(Tweet(original_tweet=Mock(retweeted_tweet=None)).is_retweet).to.be.false()
        expect(Tweet(original_tweet=Mock(retweeted_tweet=Mock())).is_retweet).to.be.true()
        expect(Tweet(original_tweet=object).is_retweet).to.be.false()

    def test_tweet_url(self):
        tweet = Tweet(original_tweet=Mock(id=123, user=Mock(screen_name='abc')))
        expect(tweet.url).to.eq('https://twitter.com/abc/status/123/')

    def test_tweet_created_at(self):
        created_at = datetime(2017, 8, 4, 14, 30, 00)
        tweet = Tweet(original_tweet=Mock(created_at=created_at))
        expect(tweet.created_at).to.eq(created_at)
