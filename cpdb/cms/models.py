from django.db import models
from django.contrib.postgres.fields import JSONField


class CMSPage(models.Model):
    slug = models.CharField(max_length=255, primary_key=True)
    descriptor_class = models.CharField(max_length=255)
    fields = JSONField()
