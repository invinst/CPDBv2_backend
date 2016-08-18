from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


LOG_TYPE_CREATE = 1
LOG_TYPE_UPDATE = 2
LOG_TYPE_DELETE = 3


class Changelog(models.Model):
    LOG_TYPE_CHOICES = (
        (LOG_TYPE_CREATE, 'Create'),
        (LOG_TYPE_UPDATE, 'Update'),
        (LOG_TYPE_DELETE, 'Delete'))

    created = models.DateTimeField(auto_now_add=True)
    target_model = models.CharField(max_length=255)
    log_type = models.IntegerField(choices=LOG_TYPE_CHOICES)
    object_pk = models.IntegerField(null=True)
    content = JSONField()
    source = JSONField()
