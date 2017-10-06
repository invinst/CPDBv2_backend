from django.test import SimpleTestCase

from robber import expect

from twitterbot.recipient_extractors import TweetAuthorRecipientExtractor, TweetMentionRecipientExtractor
from twitterbot.factories import TweetFactory, MockClientFactory


class TweetAuthorRecipientExtractorTestCase(SimpleTestCase):
    def setUp(self):
        super(TweetAuthorRecipientExtractorTestCase, self).setUp()
        self.context = {'client': MockClientFactory()}

    def test_extract(self):
        tweet1 = TweetFactory(author_screen_name='abc')
        tweet2 = TweetFactory(author_screen_name='def')
        extractor = TweetAuthorRecipientExtractor()
        expect(extractor.extract([tweet1, tweet2], self.context)).to.eq(['abc', 'def'])

    def test_remove_duplicate(self):
        tweet1 = TweetFactory(author_screen_name='abc')
        tweet2 = TweetFactory(author_screen_name='abc')
        extractor = TweetAuthorRecipientExtractor()
        expect(extractor.extract([tweet1, tweet2], self.context)).to.eq(['abc'])

    def test_exclude_self(self):
        tweet1 = TweetFactory(author_screen_name='abc')
        tweet2 = TweetFactory(author_screen_name='def')
        extractor = TweetAuthorRecipientExtractor()
        client = MockClientFactory(screen_name='def')
        expect(extractor.extract([tweet1, tweet2], {'client': client})).to.eq(['abc'])


class TweetMentionRecipientExtractorTestCase(SimpleTestCase):
    def setUp(self):
        super(TweetMentionRecipientExtractorTestCase, self).setUp()
        self.context = {'client': MockClientFactory()}

    def test_extract(self):
        tweet = TweetFactory(mentioned_screen_names=['abc'])
        extractor = TweetMentionRecipientExtractor()
        expect(extractor.extract([tweet], self.context)).to.eq(['abc'])

    def test_remove_duplicate(self):
        tweet1 = TweetFactory(mentioned_screen_names=['abc'])
        tweet2 = TweetFactory(mentioned_screen_names=['abc', 'def'])
        extractor = TweetMentionRecipientExtractor()
        expect(extractor.extract([tweet1, tweet2], self.context)).to.eq(['abc', 'def'])

    def test_exclude_self(self):
        tweet1 = TweetFactory(mentioned_screen_names=['abc'])
        tweet2 = TweetFactory(mentioned_screen_names=['def'])
        extractor = TweetMentionRecipientExtractor()
        client = MockClientFactory(screen_name='def')
        expect(extractor.extract([tweet1, tweet2], {'client': client})).to.eq(['abc'])
