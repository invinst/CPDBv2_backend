from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from .common import TimeStampsModel


class PoliceWitness(TimeStampsModel):
    allegation = models.ForeignKey('data.Allegation', on_delete=models.CASCADE, null=True)
    officer = models.ForeignKey('data.Officer', on_delete=models.CASCADE, null=True)

    objects = BulkUpdateManager()
