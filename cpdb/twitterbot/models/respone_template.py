from django.db import models

from twitterbot.constants import RESPONSE_TYPE_CHOICES
from data.models.common import TimeStampsModel


class ResponseTemplate(TimeStampsModel):
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPE_CHOICES)
    syntax = models.TextField()
