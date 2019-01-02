from django.db import models
from django.apps import apps

from twitterbot.constants import RESPONSE_TYPE_CHOICES
from data.models.common import TimeStampsModel


class TweetResponseRoundRobinManager(models.Manager):
    def get_template(self, username, response_type):
        ResponseTemplate = apps.get_app_config('twitterbot').get_model('ResponseTemplate')
        templates = ResponseTemplate.objects.filter(response_type=response_type).order_by('id')
        response_round_robin, created = self.get_or_create(username=username, response_type=response_type)
        if not created:
            response_round_robin.last_index += 1

            if response_round_robin.last_index >= templates.count():
                response_round_robin.last_index = 0

            response_round_robin.save()
        return templates[response_round_robin.last_index]


class TweetResponseRoundRobin(TimeStampsModel):
    username = models.CharField(max_length=15)
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPE_CHOICES)
    last_index = models.PositiveIntegerField(default=0)
    objects = TweetResponseRoundRobinManager()
