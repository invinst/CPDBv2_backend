from django.db import models
from django.contrib.postgres.fields import JSONField

from .constants import QUERY_TYPES


class Event(models.Model):
    name = models.CharField(max_length=255)
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SearchTracking(models.Model):
    query = models.CharField(max_length=255)
    usages = models.PositiveIntegerField(default=0)
    results = models.PositiveIntegerField(default=0)
    query_type = models.CharField(choices=QUERY_TYPES, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    last_entered = models.DateTimeField(auto_now=True)
