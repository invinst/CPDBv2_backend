from django.contrib.postgres.fields import JSONField
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    data = JSONField()
