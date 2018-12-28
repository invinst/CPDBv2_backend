from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

from data.constants import MEDIA_TYPE_CHOICES


class AttachmentFile(models.Model):
    external_id = models.CharField(max_length=255, db_index=True)
    file_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, db_index=True)
    additional_info = JSONField(null=True)
    tag = models.CharField(max_length=50)
    original_url = models.CharField(max_length=255, db_index=True)
    allegation = models.ForeignKey('data.Allegation', on_delete=models.CASCADE, related_name='attachment_files')
    source_type = models.CharField(max_length=255, db_index=True)

    # Document cloud information
    preview_image_url = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(null=True)
    last_updated = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('allegation', 'external_id', 'source_type'),)
