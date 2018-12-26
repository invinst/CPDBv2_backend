from django.contrib.gis.db import models
from django_bulk_update.manager import BulkUpdateManager

from data.validators import validate_race


class Investigator(models.Model):
    first_name = models.CharField(max_length=255, db_index=True, null=True)
    last_name = models.CharField(max_length=255, db_index=True, null=True)
    middle_initial = models.CharField(max_length=5, null=True)
    suffix_name = models.CharField(max_length=5, null=True)
    appointed_date = models.DateField(null=True)
    officer = models.ForeignKey('data.Officer', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, default='Unknown', validators=[validate_race])

    objects = BulkUpdateManager()

    @property
    def num_cases(self):
        return self.investigatorallegation_set.count()

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def abbr_name(self):
        return f'{self.first_name[0].upper()}. {self.last_name}'
