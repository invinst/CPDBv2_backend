from django.contrib.postgres.fields import ArrayField
from django.db import models


class TaggableModel(models.Model):
    tags = ArrayField(models.CharField(null=True, max_length=20), default=list)

    class Meta:
        abstract = True
