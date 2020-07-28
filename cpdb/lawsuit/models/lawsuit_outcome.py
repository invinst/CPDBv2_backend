from django.contrib.gis.db import models

from data.models.common import TimeStampsModel


class LawsuitOutcome(TimeStampsModel):
    name = models.CharField(max_length=255, db_index=True, unique=True)
