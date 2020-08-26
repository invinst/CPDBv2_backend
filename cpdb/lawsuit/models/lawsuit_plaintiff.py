from django.contrib.gis.db import models

from data.models.common import TimeStampsModel


class LawsuitPlaintiff(TimeStampsModel):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    lawsuit = models.ForeignKey('lawsuit.Lawsuit', on_delete=models.CASCADE, related_name='plaintiffs')
