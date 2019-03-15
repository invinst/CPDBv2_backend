from django.contrib.gis.db import models

from data.models.common import TimeStampsModel


class Pinboard(TimeStampsModel):
    title = models.CharField(max_length=255, default='', blank=True)
    officers = models.ManyToManyField('data.Officer')
    allegations = models.ManyToManyField('data.Allegation')
    description = models.TextField(default='', blank=True)
