from django.db import models

from twitterbot.constants import RESPONSE_TYPE_CHOICES


class ResponseTemplate(models.Model):
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPE_CHOICES)
    syntax = models.TextField()
