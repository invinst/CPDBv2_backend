from django.db import models

from document_cloud.constants import DOCUMENT_TYPES
from data.models import TimeStampsModel


class DocumentCrawler(TimeStampsModel):
    source_type = models.CharField(max_length=255)
    num_documents = models.IntegerField(default=0)
    num_new_documents = models.IntegerField(default=0)
    num_updated_documents = models.IntegerField(default=0)


class DocumentCloudSearchQuery(TimeStampsModel):
    type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    query = models.TextField()
