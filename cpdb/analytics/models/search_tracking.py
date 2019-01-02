from django.db import models

from analytics.constants import QUERY_TYPES


class SearchTracking(models.Model):
    query = models.CharField(max_length=255)
    usages = models.PositiveIntegerField(default=0)
    results = models.PositiveIntegerField(default=0)
    query_type = models.CharField(choices=QUERY_TYPES, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    last_entered = models.DateTimeField(auto_now=True)
