from django.contrib.gis.db import models

from .common import TimeStampsModel


class AttachmentNarrative(TimeStampsModel):
    attachment = models.ForeignKey(
        'data.AttachmentFile', on_delete=models.CASCADE, related_name='attachment_narratives'
    )
    page_num = models.IntegerField()
    section_name = models.CharField(max_length=255)
    column_name = models.CharField(max_length=255)
    text_content = models.TextField(blank=True)
