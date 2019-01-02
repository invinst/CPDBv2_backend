from django.contrib.gis.db import models

from .common import TimeStampsModel


class RacePopulation(TimeStampsModel):
    race = models.CharField(max_length=255)
    count = models.PositiveIntegerField()
    area = models.ForeignKey('data.Area', on_delete=models.CASCADE)
