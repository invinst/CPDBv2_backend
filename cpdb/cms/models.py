from django.db import models
from django.contrib.postgres.fields import JSONField


class SlugPage(models.Model):
    slug = models.CharField(max_length=255, primary_key=True)
    descriptor_class = models.CharField(max_length=255)
    fields = JSONField()


class ReportPage(models.Model):
    descriptor_class = models.CharField(max_length=255)
    fields = JSONField()
