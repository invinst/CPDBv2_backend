from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from data.models.common import TimeStampsModel
from activity_log.constants import ACTION_TYPE_CHOICES


class ActivityLog(TimeStampsModel):
    modified_object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    modified_object_id = models.PositiveIntegerField()
    modified_object = GenericForeignKey('modified_object_type', 'modified_object_id')
    action_type = models.CharField(max_length=255, choices=ACTION_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField()
