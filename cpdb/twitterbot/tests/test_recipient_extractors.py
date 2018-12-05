from django.test import SimpleTestCase

from robber import expect

from twitterbot.recipient_extractors import TweetAuthorRecipientExtractor, TweetMentionRecipientExtractor
from twitterbot.factories import TweetFactory, MockTweepyWrapperFactory


class TweetAuthorRecipientExtractorTestCase(SimpleTestCase):
    def setUp(self):
        super(TweetAuthorRecipientExtractorTestCase, self).setUp()
        self.context = {'client': MockTweepyWrapperFactory(), 'for_user_id': 123}

    def test_extract(self):
        tweet1 = TweetFactory(author_screen_name='abc')
        tweet2 = TweetFactory(author_screen_name='def')
        extractor = TweetAuthorRecipientExtractor()
        expect(set(extractor.extract([tweet1, tweet2], self.context))).to.eq(set(['abc', 'def']))

    def test_remove_duplicate(self):
        tweet1 = TweetFactory(author_screen_name='abc')
        tweet2 = TweetFactory(author_screen_name='abc')
        extractor = TweetAuthorRecipientExtractor()
        expect(extractor.extract([tweet1, tweet2], self.context)).to.eq(['abc'])

    def test_exclude_self(self):
        tweet1 = TweetFactory(author_screen_name='abc')
        tweet2 = TweetFactory(author_screen_name='def', id=123)
        extractor = TweetAuthorRecipientExtractor()
        client = MockTweepyWrapperFactory(subscription_screen_name='def')
        expect(extractor.extract([tweet1, tweet2], {'client': client, 'for_user_id': 123})).to.eq(['abc'])


class TweetMentionRecipientExtractorTestCase(SimpleTestCase):
    def setUp(self):
        super(TweetMentionRecipientExtractorTestCase, self).setUp()
        self.context = {'client': MockTweepyWrapperFactory(), 'for_user_id': 123}

    def test_extract(self):
        tweet = TweetFactory(user_mentions=[{'screen_name': 'abc'}])
        extractor = TweetMentionRecipientExtractor()
        expect(extractor.extract([tweet], self.context)).to.eq(['abc'])

    def test_remove_duplicate(self):
        tweet1 = TweetFactory(user_mentions=[{'screen_name': 'abc'}])
        tweet2 = TweetFactory(user_mentions=[{'screen_name': 'abc'}, {'screen_name': 'def'}])
        extractor = TweetMentionRecipientExtractor()
        expect(set(extractor.extract([tweet1, tweet2], self.context))).to.eq(set(['abc', 'def']))

    def test_exclude_self(self):
        tweet1 = TweetFactory(user_mentions=[{'screen_name': 'abc'}])
        tweet2 = TweetFactory(user_mentions=[{'screen_name': 'def'}], id=123)
        extractor = TweetMentionRecipientExtractor()
        client = MockTweepyWrapperFactory(subscription_screen_name='def')
        expect(extractor.extract([tweet1, tweet2], {'client': client, 'for_user_id': 123})).to.eq(['abc'])
