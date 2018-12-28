from django.contrib.gis.db import models


class RacePopulation(models.Model):
    race = models.CharField(max_length=255)
    count = models.PositiveIntegerField()
    area = models.ForeignKey('data.Area', on_delete=models.CASCADE)
