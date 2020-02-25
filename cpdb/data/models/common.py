from django.db import models

from taggit.managers import TaggableManager


class TaggableModel(models.Model):
    tags = TaggableManager(blank=True)

    class Meta:
        abstract = True


class TimeStampsModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
