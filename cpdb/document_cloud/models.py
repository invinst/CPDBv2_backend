from django.db import models

from document_cloud.constants import DOCUMENT_TYPES


class DocumentCrawler(models.Model):
    source_type = models.CharField(max_length=255)
    num_documents = models.IntegerField(default=0)
    num_new_documents = models.IntegerField(default=0)
    num_updated_documents = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class DocumentCloudSearchQuery(models.Model):
    type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    query = models.TextField()
