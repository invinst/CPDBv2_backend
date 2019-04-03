from django.contrib.gis.db import models

from data.models.common import TimeStampsModel
from pinboard.fields import HexField


class Pinboard(TimeStampsModel):
    id = HexField(hex_length=8, primary_key=True)
    title = models.CharField(max_length=255, default='', blank=True)
    officers = models.ManyToManyField('data.Officer')
    allegations = models.ManyToManyField('data.Allegation')
    trrs = models.ManyToManyField('trr.TRR')
    description = models.TextField(default='', blank=True)
