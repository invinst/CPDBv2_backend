from django.db import models

from data.models.common import TimeStampsModel


class DocumentCrawler(TimeStampsModel):
    source_type = models.CharField(max_length=255)
    num_documents = models.IntegerField(default=0)
    num_new_documents = models.IntegerField(default=0)
    num_updated_documents = models.IntegerField(default=0)
