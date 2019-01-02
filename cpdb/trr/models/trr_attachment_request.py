from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from data.models.common import TimeStampsModel


class TRRAttachmentRequest(TimeStampsModel):
    trr = models.ForeignKey('trr.TRR', on_delete=models.CASCADE)
    email = models.EmailField(max_length=255)
    status = models.BooleanField(default=False)
    airtable_id = models.CharField(max_length=255, blank=True, default='')

    objects = BulkUpdateManager()

    class Meta:
        unique_together = (('trr', 'email'),)

    def __str__(self):
        return f'{self.email} - {self.trr.id}'
