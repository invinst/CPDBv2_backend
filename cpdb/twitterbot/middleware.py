import logging

from .models import TwitterBotResponseLog

logger = logging.getLogger(__name__)


class LogTwitterbotLinkVisitMiddleware:
    def process_request(self, request):
        param = 'twitterbot_log_id'
        if param in request.GET:
            logger.info('%s - Someone visit %s from status %s' % (
                self.__class__.__name__, request.path,
                TwitterBotResponseLog.objects.get(id=request.GET[param]).tweet_url))
        return None
