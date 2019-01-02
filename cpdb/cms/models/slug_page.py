from django.db import models
from django.contrib.postgres.fields import JSONField

from data.models.common import TimeStampsModel


class SlugPage(TimeStampsModel):
    slug = models.CharField(max_length=255, primary_key=True)
    serializer_class = models.CharField(max_length=255)
    fields = JSONField()
