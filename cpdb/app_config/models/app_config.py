from django.db import models

from data.models.common import TimeStampsModel


class AppConfig(TimeStampsModel):
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=64)
    description = models.TextField()

    def __str__(self):
        return f'{self.name}: {self.value}'
