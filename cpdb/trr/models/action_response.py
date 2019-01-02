from django.contrib.gis.db import models

from trr.constants import (
    ACTION_PERSON_CHOICES,
    RESISTANCE_TYPE_CHOICES,
    RESISTANCE_LEVEL_CHOICES,
)
from data.models.common import TimeStampsModel


class ActionResponse(TimeStampsModel):
    trr = models.ForeignKey('trr.TRR', on_delete=models.CASCADE)
    person = models.CharField(max_length=16, null=True, choices=ACTION_PERSON_CHOICES)
    resistance_type = models.CharField(max_length=32, null=True, choices=RESISTANCE_TYPE_CHOICES)
    action = models.CharField(max_length=64, null=True)
    other_description = models.CharField(max_length=64, null=True)
    member_action = models.CharField(max_length=64, null=True)
    force_type = models.CharField(max_length=64, null=True)
    action_sub_category = models.CharField(max_length=3, null=True)
    action_category = models.CharField(max_length=1, null=True)
    resistance_level = models.CharField(max_length=16, null=True, choices=RESISTANCE_LEVEL_CHOICES)
