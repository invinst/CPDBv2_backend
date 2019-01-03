from django.db import models

from data.models.common import TimeStampsModel


class TwitterBotVisitLog(TimeStampsModel):
    response_log = models.ForeignKey('twitterbot.TwitterBotResponseLog', on_delete=models.CASCADE)
    request_path = models.CharField(max_length=255)
