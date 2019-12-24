from django.db import models

from data.models.common import TimeStampsModel


class Toast(TimeStampsModel):
    name = models.CharField(max_length=25)
    template = models.TextField(
        help_text='Markdown supported'
    )
    tags = models.CharField(
        max_length=255,
        help_text='This is a list of tags available, please leave this field as is.',
    )

    def __str__(self):
        return self.name
