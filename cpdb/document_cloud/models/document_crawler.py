from django.db import models

from data.models.common import TimeStampsModel
from document_cloud.constants import DOCUMENT_CRAWLER_STATUS_CHOICES


class DocumentCrawler(TimeStampsModel):
    source_type = models.CharField(max_length=255)
    num_documents = models.IntegerField(default=0)
    num_new_documents = models.IntegerField(default=0)
    num_successful_run = models.IntegerField(default=0)
    num_updated_documents = models.IntegerField(default=0)
    status = models.CharField(max_length=20, null=True, choices=DOCUMENT_CRAWLER_STATUS_CHOICES)
