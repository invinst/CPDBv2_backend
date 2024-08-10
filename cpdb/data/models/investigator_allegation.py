from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from .common import TimeStampsModel


class InvestigatorAllegation(TimeStampsModel):
    investigator = models.ForeignKey('data.Investigator', on_delete=models.CASCADE)
    allegation = models.ForeignKey('data.Allegation', on_delete=models.CASCADE)
    current_star = models.CharField(max_length=10, null=True)
    current_rank = models.CharField(max_length=100, null=True)
    current_unit = models.ForeignKey('data.PoliceUnit', on_delete=models.SET_NULL, null=True)
    investigator_type = models.CharField(max_length=32, null=True)
    investigating_agency = models.CharField(max_length=32, null=True)

    objects = BulkUpdateManager()
