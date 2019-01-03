from django.db import models

from document_cloud.constants import DOCUMENT_TYPES
from data.models.common import TimeStampsModel


class DocumentCloudSearchQuery(TimeStampsModel):
    type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    query = models.TextField()
