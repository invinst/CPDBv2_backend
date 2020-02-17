from django.contrib.gis.db import models

from .common import TimeStampsModel


class Tag(TimeStampsModel):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ['name']
