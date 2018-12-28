from django.contrib.gis.db import models


class SubjectWeapon(models.Model):
    trr = models.ForeignKey('trr.TRR', on_delete=models.CASCADE)
    weapon_type = models.CharField(max_length=64, null=True)
    firearm_caliber = models.CharField(max_length=16, null=True)
    weapon_description = models.CharField(max_length=64, null=True)
