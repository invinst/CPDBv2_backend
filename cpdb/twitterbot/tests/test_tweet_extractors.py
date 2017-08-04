from django.test import SimpleTestCase

from robber import expect

from twitterbot.tweet_extractors import RelatedTweetExtractor
from twitterbot.factories import TweetFactory, MockClientFactory


class RelatedTweetExtractorTestCase(SimpleTestCase):
    def test_extract_replied_tweet(self):
        extractor = RelatedTweetExtractor()
        client = MockClientFactory()
        replied_tweet = TweetFactory(client=client)
        client.register(replied_tweet)
        tweet = TweetFactory(in_reply_to_tweet=replied_tweet, client=client)
        tweet_ids = [t.id for t in extractor.extract(tweet, context={'client': client})]
        expect(tweet_ids).to.eq([tweet.id, replied_tweet.id])

    def test_extract_retweeted_tweet(self):
        extractor = RelatedTweetExtractor()
        client = MockClientFactory()
        retweeted_tweet = TweetFactory(client=client)
        client.register(retweeted_tweet)
        tweet = TweetFactory(retweeted_tweet=retweeted_tweet, client=client)
        tweet_ids = [t.id for t in extractor.extract(tweet, context={'client': client})]
        expect(tweet_ids).to.eq([tweet.id, retweeted_tweet.id])

    def test_extract_quoted_tweet(self):
        extractor = RelatedTweetExtractor()
        client = MockClientFactory()
        quoted_tweet = TweetFactory(client=client)
        client.register(quoted_tweet)
        tweet = TweetFactory(quoted_tweet=quoted_tweet, client=client)
        tweet_ids = [t.id for t in extractor.extract(tweet, context={'client': client})]
        expect(tweet_ids).to.eq([tweet.id, quoted_tweet.id])

    def test_extract_nested_tweet(self):
        extractor = RelatedTweetExtractor()
        client = MockClientFactory()
        nested_replied_tweet = TweetFactory(client=client)
        client.register(nested_replied_tweet)
        replied_tweet = TweetFactory(in_reply_to_tweet=nested_replied_tweet, client=client)
        client.register(replied_tweet)
        tweet = TweetFactory(in_reply_to_tweet=replied_tweet, client=client)
        tweet_ids = [t.id for t in extractor.extract(tweet, context={'client': client})]
        expect(tweet_ids).to.eq([tweet.id, replied_tweet.id, nested_replied_tweet.id])

    def test_exclude_self_tweet(self):
        extractor = RelatedTweetExtractor()
        client = MockClientFactory()
        replied_tweet = TweetFactory(user_id=111, client=client)
        client.register(replied_tweet)
        tweet = TweetFactory(in_reply_to_tweet=replied_tweet, client=client)
        tweet_ids = [t.id for t in extractor.extract(tweet, context={'client': client})]
        expect(tweet_ids).to.eq([tweet.id])

    def test_populate_first_non_retweet(self):
        extractor = RelatedTweetExtractor()
        client = MockClientFactory()
        retweeted_tweet = TweetFactory(client=client)
        client.register(retweeted_tweet)
        tweet = TweetFactory(retweeted_tweet=retweeted_tweet, client=client)
        context = {'client': client}
        extractor.extract(tweet, context=context)
        expect(context['first_non_retweet'].id).to.eq(retweeted_tweet.id)
