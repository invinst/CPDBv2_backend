from django.db import models


class TwitterBotVisitLog(models.Model):
    response_log = models.ForeignKey('twitterbot.TwitterBotResponseLog', on_delete=models.CASCADE)
    request_path = models.CharField(max_length=255)
