from django.contrib.gis.db import models

from trr.constants import TRR_STATUS_CHOICES


class TRRStatus(models.Model):
    trr = models.ForeignKey('trr.TRR', on_delete=models.CASCADE)
    officer = models.ForeignKey('data.officer', on_delete=models.CASCADE, null=True)
    rank = models.CharField(max_length=16, null=True)
    star = models.CharField(max_length=10, null=True)
    status = models.CharField(max_length=16, null=True, choices=TRR_STATUS_CHOICES)
    status_datetime = models.DateTimeField(null=True)
    age = models.SmallIntegerField(null=True)
