from django.contrib.postgres.fields import JSONField
from django.db import models

from data.models.common import TimeStampsModel


class Event(TimeStampsModel):
    name = models.CharField(max_length=255)
    data = JSONField()
