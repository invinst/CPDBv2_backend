from django.contrib.gis.db import models

from .common import TimeStampsModel


class AttachmentOCR(TimeStampsModel):
    attachment = models.ForeignKey('data.AttachmentFile', on_delete=models.CASCADE, related_name='attachment_ocrs')
    page_num = models.IntegerField()
    ocr_text = models.TextField(blank=True)
