from django.db import models
from django.contrib.postgres.fields import JSONField

from data.models import TaggableModel, Officer


class SlugPage(models.Model):
    slug = models.CharField(max_length=255, primary_key=True)
    serializer_class = models.CharField(max_length=255)
    fields = JSONField()


class ReportPage(TaggableModel):
    fields = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    officers = models.ManyToManyField(Officer)
