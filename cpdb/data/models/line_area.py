from django.contrib.gis.db import models

from data.constants import LINE_AREA_CHOICES


class LineArea(models.Model):
    name = models.CharField(max_length=100)
    linearea_type = models.CharField(max_length=30, choices=LINE_AREA_CHOICES)
    geom = models.MultiLineStringField(srid=4326, blank=True)
