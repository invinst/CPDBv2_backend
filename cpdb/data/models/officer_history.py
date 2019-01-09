from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from .common import TimeStampsModel


class OfficerHistory(TimeStampsModel):
    officer = models.ForeignKey('data.Officer', on_delete=models.CASCADE, null=True)
    unit = models.ForeignKey('data.PoliceUnit', on_delete=models.CASCADE, null=True)
    effective_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    objects = BulkUpdateManager()

    class Meta:
        indexes = [
            models.Index(fields=['end_date']),
            models.Index(fields=['effective_date']),
        ]

    @property
    def unit_name(self):
        return self.unit.unit_name

    @property
    def unit_description(self):
        return self.unit.description
