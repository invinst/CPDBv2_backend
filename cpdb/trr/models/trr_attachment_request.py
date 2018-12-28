from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager


class TRRAttachmentRequest(models.Model):
    trr = models.ForeignKey('trr.TRR', on_delete=models.CASCADE)
    email = models.EmailField(max_length=255)
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    airtable_id = models.CharField(max_length=255, blank=True, default='')

    objects = BulkUpdateManager()

    class Meta:
        unique_together = (('trr', 'email'),)

    def __str__(self):
        return f'{self.email} - {self.trr.id}'
