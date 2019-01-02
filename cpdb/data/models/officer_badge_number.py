from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from .common import TimeStampsModel


class OfficerBadgeNumber(TimeStampsModel):
    officer = models.ForeignKey('data.Officer', on_delete=models.CASCADE, null=True)
    star = models.CharField(max_length=10)
    current = models.BooleanField(default=False)

    objects = BulkUpdateManager()

    class Meta:
        indexes = [
            models.Index(fields=['current']),
        ]

    def __str__(self):
        return f'{self.officer} - {self.star}'
