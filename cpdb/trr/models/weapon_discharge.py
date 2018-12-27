from django.contrib.gis.db import models

from trr.constants import (
    HANDGUN_WORN_TYPE_CHOICES,
    HANDGUN_DRAWN_TYPE_CHOICES,
    OBJECT_STRUCK_OF_DISCHARGE_CHOICES,
    DISCHARGE_POSITION_CHOICES,
)


class WeaponDischarge(models.Model):
    trr = models.ForeignKey('trr.TRR', on_delete=models.CASCADE)
    weapon_type = models.CharField(max_length=32, null=True)
    weapon_type_description = models.CharField(max_length=32, null=True)
    firearm_make = models.CharField(max_length=64, null=True)
    firearm_model = models.CharField(max_length=32, null=True)
    firearm_barrel_length = models.CharField(max_length=16, null=True)
    firearm_caliber = models.CharField(max_length=16, null=True)
    total_number_of_shots = models.SmallIntegerField(null=True)
    firearm_reloaded = models.NullBooleanField()
    number_of_catdridge_reloaded = models.SmallIntegerField(null=True)
    handgun_worn_type = models.CharField(max_length=32, null=True, choices=HANDGUN_WORN_TYPE_CHOICES)
    handgun_drawn_type = models.CharField(max_length=32, null=True, choices=HANDGUN_DRAWN_TYPE_CHOICES)
    method_used_to_reload = models.CharField(max_length=64, null=True)
    sight_used = models.NullBooleanField()
    protective_cover_used = models.CharField(max_length=32, null=True)
    discharge_distance = models.CharField(max_length=16, null=True)
    object_struck_of_discharge = models.CharField(max_length=32, null=True, choices=OBJECT_STRUCK_OF_DISCHARGE_CHOICES)
    discharge_position = models.CharField(max_length=32, null=True, choices=DISCHARGE_POSITION_CHOICES)
