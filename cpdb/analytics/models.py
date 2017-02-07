from django.db import models
from django.contrib.postgres.fields import JSONField


class Event(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    data = JSONField()
