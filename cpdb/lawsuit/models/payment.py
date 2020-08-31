from django.contrib.gis.db import models

from data.models.common import TimeStampsModel


class Payment(TimeStampsModel):
    payee = models.CharField(max_length=255)
    settlement = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    legal_fees = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    lawsuit = models.ForeignKey('lawsuit.Lawsuit', on_delete=models.CASCADE, related_name='payments')
