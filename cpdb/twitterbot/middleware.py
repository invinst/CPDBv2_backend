import logging

from .models import TwitterBotResponseLog, TwitterBotVisitLog

logger = logging.getLogger(__name__)


class LogTwitterbotLinkVisitMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        param = 'twitterbot_log_id'
        if param in request.GET:
            response_log = TwitterBotResponseLog.objects.get(id=request.GET[param])
            logger.info('%s - Someone visit %s from status %s' % (
                self.__class__.__name__, request.path, response_log.tweet_url))
            TwitterBotVisitLog.objects.create(request_path=request.path, response_log=response_log)

        response = self.get_response(request)

        return response
