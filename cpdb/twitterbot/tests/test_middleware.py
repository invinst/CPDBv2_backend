from django.test import TestCase

from mock import Mock, patch
from robber import expect

from twitterbot.middleware import LogTwitterbotLinkVisitMiddleware
from twitterbot.factories import TwitterBotResponseLogFactory
from twitterbot.models import TwitterBotVisitLog


class LogTwitterbotLinkVisitMiddlewareTestCase(TestCase):
    def test_log_twitterbot_link(self):
        response = Mock()
        get_response = Mock(return_value=response)
        middleware = LogTwitterbotLinkVisitMiddleware(get_response)
        request = Mock(GET={'twitterbot_log_id': 123}, path='/foo/')
        tweet_url = 'http://t.co/status/123/'
        response_log = TwitterBotResponseLogFactory(id=123, tweet_url=tweet_url)
        expect(TwitterBotVisitLog.objects.count()).to.equal(0)
        with patch('twitterbot.middleware.logger.info') as info:
            expect(middleware(request)).to.eq(response)
            info.assert_called_with(f'LogTwitterbotLinkVisitMiddleware - Someone visit /foo/ from status {tweet_url}')
        expect(TwitterBotVisitLog.objects.count()).to.equal(1)
        visit_log = TwitterBotVisitLog.objects.first()
        expect(visit_log.request_path).to.eq('/foo/')
        expect(visit_log.response_log).to.eq(response_log)

    def test_no_log(self):
        response = Mock()
        get_response = Mock(return_value=response)
        middleware = LogTwitterbotLinkVisitMiddleware(get_response)
        request = Mock(GET={}, path='/foo/')
        with patch('twitterbot.middleware.logger.info') as info:
            expect(middleware(request)).to.eq(response)
            info.assert_not_called()
