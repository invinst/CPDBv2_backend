from django.db import models

from data.models import TimeStampsModel


class Popup(TimeStampsModel):
    name = models.CharField(max_length=64)
    page = models.CharField(max_length=32)
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.name
