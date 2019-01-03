from django.db import models

from data.models.common import TimeStampsModel


class ActivityCard(TimeStampsModel):
    officer = models.OneToOneField('data.Officer', on_delete=models.CASCADE, related_name='activity_card')
    important = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True)
