from django.db import models
from django.contrib.postgres.fields import JSONField

from data.models import Officer


class SlugPage(models.Model):
    slug = models.CharField(max_length=255, primary_key=True)
    serializer_class = models.CharField(max_length=255)
    fields = JSONField()


class ReportPage(models.Model):
    fields = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    officers = models.ManyToManyField(Officer)


class FAQPage(models.Model):
    fields = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)
    starred = models.BooleanField(default=False)
