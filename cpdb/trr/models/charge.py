from django.contrib.gis.db import models

from data.models.common import TimeStampsModel


class Charge(TimeStampsModel):
    trr = models.ForeignKey('trr.TRR', on_delete=models.CASCADE)
    sr_no = models.PositiveIntegerField(null=True)
    statute = models.CharField(max_length=64, null=True)
    description = models.CharField(max_length=64, null=True)
    subject_no = models.PositiveIntegerField(null=True)
