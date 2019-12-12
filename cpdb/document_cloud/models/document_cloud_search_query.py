from django.db import models

from document_cloud.constants import DOCUMENT_TYPES
from data.models.common import TimeStampsModel
from utils.models.choice_array_field import ChoiceArrayField


class DocumentCloudSearchQuery(TimeStampsModel):
    types = ChoiceArrayField(models.CharField(max_length=20, choices=DOCUMENT_TYPES), default=list)
    query = models.TextField()
