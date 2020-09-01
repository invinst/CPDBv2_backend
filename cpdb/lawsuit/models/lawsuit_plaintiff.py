from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from data.models.common import TimeStampsModel


class LawsuitPlaintiff(TimeStampsModel):
    name = models.CharField(max_length=255)
    lawsuit = models.ForeignKey('lawsuit.Lawsuit', on_delete=models.CASCADE, related_name='plaintiffs')
    airtable_id = models.CharField(max_length=20, db_index=True, unique=True, null=True)
    airtable_updated_at = models.CharField(max_length=30, null=True, blank=True)

    objects = models.Manager()
    bulk_objects = BulkUpdateManager()
