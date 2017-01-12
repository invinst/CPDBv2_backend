from django.db import models
from django.contrib.postgres.fields import JSONField


class SlugPage(models.Model):
    slug = models.CharField(max_length=255, primary_key=True)
    serializer_class = models.CharField(max_length=255)
    fields = JSONField()


class ReportPage(models.Model):
    fields = JSONField()
    created = models.DateTimeField(auto_now_add=True)


class FAQPage(models.Model):
    fields = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)
