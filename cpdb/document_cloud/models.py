from django.db import models

from document_cloud.constants import DOCUMENT_TYPES


class DocumentCrawler(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    num_documents = models.IntegerField()


class DocumentCloudSearchQuery(models.Model):
    type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    query = models.TextField()
