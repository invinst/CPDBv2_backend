from django.contrib.gis.db import models

from data.models.common import TimeStampsModel


class SubjectWeapon(TimeStampsModel):
    trr = models.ForeignKey('trr.TRR', on_delete=models.CASCADE)
    weapon_type = models.CharField(max_length=64, null=True)
    firearm_caliber = models.CharField(max_length=16, null=True)
    weapon_description = models.CharField(max_length=64, null=True)
