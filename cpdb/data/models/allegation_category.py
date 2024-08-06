from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from data.constants import CITIZEN_DEPTS, CITIZEN_CHOICE
from .common import TimeStampsModel


class AllegationCategory(TimeStampsModel):
    category_code = models.CharField(max_length=255)
    category = models.CharField(max_length=255, db_index=True, blank=True)
    allegation_name = models.CharField(max_length=255, blank=True)
    on_duty = models.BooleanField(default=False)
    citizen_dept = models.CharField(max_length=50, default=CITIZEN_CHOICE, choices=CITIZEN_DEPTS)

    objects = BulkUpdateManager()
