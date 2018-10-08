from django.test import SimpleTestCase

from robber import expect
from mock import Mock, patch

from twitterbot.tweet_extractors import RelatedTweetExtractor, DirectMentionTweetExtractor
from twitterbot.factories import TweetFactory, MockTweepyWrapperFactory


class RelatedTweetExtractorTestCase(SimpleTestCase):
    def setUp(self):
        self.extractor = RelatedTweetExtractor()
        self.client = MockTweepyWrapperFactory()
        self.context = {
            'client': self.client,
            'for_user_id': 111
        }

    def test_extract_replied_tweet(self):
        replied_tweet = TweetFactory(context=self.context)
        self.client.register(replied_tweet)
        tweet = TweetFactory(in_reply_to_tweet=replied_tweet, context=self.context)
        tweet_ids = [t.id for t in self.extractor.extract(tweet, context=self.context)]
        expect(tweet_ids).to.eq([tweet.id, replied_tweet.id])

    def test_extract_retweeted_status(self):
        retweeted_status = TweetFactory(context=self.context)
        self.client.register(retweeted_status)
        tweet = TweetFactory(retweeted_status=retweeted_status, context=self.context)
        tweet_ids = [t.id for t in self.extractor.extract(tweet, context=self.context)]
        expect(tweet_ids).to.eq([tweet.id, retweeted_status.id])

    def test_extract_quoted_tweet(self):
        quoted_tweet = TweetFactory(context=self.context)
        self.client.register(quoted_tweet)
        tweet = TweetFactory(quoted_tweet=quoted_tweet, context=self.context)
        tweet_ids = [t.id for t in self.extractor.extract(tweet, context=self.context)]
        expect(tweet_ids).to.eq([tweet.id, quoted_tweet.id])

    def test_extract_nested_tweet(self):
        nested_replied_tweet = TweetFactory(context=self.context)
        self.client.register(nested_replied_tweet)
        replied_tweet = TweetFactory(in_reply_to_tweet=nested_replied_tweet, context=self.context)
        self.client.register(replied_tweet)
        tweet = TweetFactory(in_reply_to_tweet=replied_tweet, context=self.context)
        tweet_ids = [t.id for t in self.extractor.extract(tweet, context=self.context)]
        expect(tweet_ids).to.eq([tweet.id, replied_tweet.id, nested_replied_tweet.id])

    def test_exclude_self_tweet(self):
        replied_tweet = TweetFactory(user_id=111, context=self.context)
        self.client.register(replied_tweet)
        tweet = TweetFactory(in_reply_to_tweet=replied_tweet, context=self.context)
        tweet_ids = [t.id for t in self.extractor.extract(tweet, context=self.context)]
        expect(tweet_ids).to.eq([tweet.id])

    def test_populate_first_non_retweet(self):
        retweeted_status = TweetFactory(context=self.context)
        self.client.register(retweeted_status)
        tweet = TweetFactory(retweeted_status=retweeted_status, context=self.context)
        self.extractor.extract(tweet, context=self.context)
        expect(self.context['first_non_retweet'].id).to.eq(retweeted_status.id)

    def test_populate_first_non_retweet_got_none(self):
        tweet = Mock()
        context = {}
        with patch('twitterbot.tweet_extractors.RelatedTweetExtractor.get_tweets', return_value=[]):
            self.extractor.extract(tweet, context=self.context)
            expect(context.get('first_non_retweet', None)).to.be.none()

    def test_populate_original_tweet(self):
        retweeted_status = TweetFactory(context=self.context, created_at='2010-02-03T11:59:00Z')
        self.client.register(retweeted_status)
        tweet = TweetFactory(retweeted_status=retweeted_status, context=self.context)
        self.extractor.extract(tweet, context=self.context)
        expect(self.context['original_tweet'].id).to.eq(retweeted_status.id)

    @patch.object(RelatedTweetExtractor, 'get_tweets', return_value=[])
    def test_populate_original_tweet_got_none(self, extractor):
        tweet = Mock()
        context = {}
        extractor.extract(tweet, context=context)
        expect(context.get('original_tweet', None)).to.be.none()


class DirectMentionTweetExtractorTestCase(SimpleTestCase):
    def setUp(self):
        self.extractor = DirectMentionTweetExtractor()
        self.context = {
            'client': MockTweepyWrapperFactory(),
            'for_user_id': 123
        }

    def test_extract_direct_mention(self):
        tweet = TweetFactory(context=self.context, user_mentions=[{'id': 123}])
        tweet_ids = [t.id for t in self.extractor.extract(tweet, context=self.context)]
        expect(tweet_ids).to.eq([tweet.id])

    def test_extract_not_direct_mention(self):
        tweet = TweetFactory(context=self.context, user_mentions=[])
        tweet_ids = [t.id for t in self.extractor.extract(tweet, context=self.context)]
        expect(tweet_ids).to.eq([])
