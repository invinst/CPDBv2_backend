from django.test import TestCase

from mock import Mock
from robber import expect

from twitterbot.models import TwitterBotResponseLog
from twitterbot.response_loggers import DatabaseResponseLogger


class DatabaseResponseLoggerTestCase(TestCase):
    def test_log_response(self):
        response = (('source1', 'source2'), 'tweet_content', 'http://entityurl.com')
        outgoing_tweet = Mock(id=1, user=Mock(screen_name='xyz'))
        context = {
            'original_tweet': Mock(screen_name='abc', url='http://original.com', text='original tweet content'),
            'incoming_tweet': Mock(screen_name='def', url='http://incoming.com', text='incoming tweet content')
        }

        expect(TwitterBotResponseLog.objects.count()).to.eq(0)

        logger = DatabaseResponseLogger()
        logger.log_response(response, outgoing_tweet, context)

        expect(TwitterBotResponseLog.objects.count()).to.eq(1)

        response_log = TwitterBotResponseLog.objects.first()
        expect(response_log.sources).to.eq('source1, source2')
        expect(response_log.tweet_content).to.eq('tweet_content')
        expect(response_log.entity_url).to.eq('http://entityurl.com')
        expect(response_log.tweet_url).to.eq('https://twitter.com/xyz/status/1/')
        expect(response_log.incoming_tweet_username).to.eq('def')
        expect(response_log.incoming_tweet_url).to.eq('http://incoming.com')
        expect(response_log.incoming_tweet_content).to.eq('incoming tweet content')
        expect(response_log.original_tweet_username).to.eq('abc')
        expect(response_log.original_tweet_url).to.eq('http://original.com')
        expect(response_log.original_tweet_content).to.eq('original tweet content')
