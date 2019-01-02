from django.contrib.gis.db import models

from data.constants import GENDER_DICT
from data.validators import validate_race
from .common import TimeStampsModel


class Involvement(TimeStampsModel):
    allegation = models.ForeignKey('data.Allegation', on_delete=models.CASCADE)
    officer = models.ForeignKey('data.Officer', on_delete=models.SET_NULL, null=True)
    full_name = models.CharField(max_length=50)
    involved_type = models.CharField(max_length=25)
    gender = models.CharField(max_length=1, null=True)
    race = models.CharField(max_length=50, default='Unknown', validators=[validate_race])
    age = models.IntegerField(null=True)

    @property
    def gender_display(self):
        try:
            return GENDER_DICT[self.gender]
        except KeyError:
            return self.gender
