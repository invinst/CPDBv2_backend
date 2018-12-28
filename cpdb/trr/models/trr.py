from django.contrib.gis.db import models

from data.constants import GENDER
from trr.constants import (
    DIRECTION_CHOICES,
    INDOOR_OUTDOOR_CHOICES,
    LIGHTNING_CONDITION_CHOICES,
    WEATHER_CONDITION_CHOICES,
    PARTY_FIRED_FIRST_CHOICES,
)


class TRR(models.Model):
    beat = models.PositiveSmallIntegerField(null=True)
    block = models.CharField(max_length=8, null=True)
    direction = models.CharField(max_length=8, null=True, choices=DIRECTION_CHOICES)
    street = models.CharField(max_length=64, null=True)
    location = models.CharField(max_length=64, null=True)
    trr_datetime = models.DateTimeField(null=True)
    indoor_or_outdoor = models.CharField(max_length=8, null=True, choices=INDOOR_OUTDOOR_CHOICES)
    lighting_condition = models.CharField(max_length=32, null=True, choices=LIGHTNING_CONDITION_CHOICES)
    weather_condition = models.CharField(max_length=32, null=True, choices=WEATHER_CONDITION_CHOICES)
    notify_OEMC = models.NullBooleanField()
    notify_district_sergeant = models.NullBooleanField()
    notify_OP_command = models.NullBooleanField()
    notify_DET_division = models.NullBooleanField()
    number_of_weapons_discharged = models.PositiveSmallIntegerField(null=True)
    party_fired_first = models.CharField(max_length=16, null=True, choices=PARTY_FIRED_FIRST_CHOICES)
    location_recode = models.CharField(max_length=64, null=True)
    taser = models.NullBooleanField()
    total_number_of_shots = models.PositiveSmallIntegerField(null=True)
    firearm_used = models.NullBooleanField()
    number_of_officers_using_firearm = models.PositiveSmallIntegerField(null=True)
    point = models.PointField(srid=4326, null=True)
    officer = models.ForeignKey('data.Officer', on_delete=models.CASCADE, null=True)
    officer_assigned_beat = models.CharField(max_length=16, null=True)
    officer_unit = models.ForeignKey('data.PoliceUnit', on_delete=models.SET_NULL, null=True)
    officer_unit_detail = models.ForeignKey(
        'data.PoliceUnit', on_delete=models.SET_NULL, null=True, related_name='trr_unit_detail_reverse')
    officer_on_duty = models.NullBooleanField()
    officer_in_uniform = models.NullBooleanField()
    officer_injured = models.NullBooleanField()
    officer_rank = models.CharField(max_length=32, null=True)
    subject_id = models.PositiveIntegerField(null=True)
    subject_armed = models.NullBooleanField()
    subject_injured = models.NullBooleanField()
    subject_alleged_injury = models.NullBooleanField()
    subject_age = models.PositiveSmallIntegerField(null=True)
    subject_birth_year = models.PositiveSmallIntegerField(null=True)
    subject_gender = models.CharField(max_length=1, null=True, choices=GENDER)
    subject_race = models.CharField(max_length=32, null=True)

    @property
    def force_category(self):
        return 'Taser' if self.taser else 'Firearm' if self.firearm_used else 'Other'

    @property
    def _member_actions(self):
        return self.actionresponse_set.filter(person='Member Action').\
            order_by('-action_sub_category', 'force_type')

    @property
    def force_types(self):
        return self._member_actions.values_list('force_type', flat=True).distinct()

    @property
    def top_force_type(self):
        top_action = self._member_actions.first()
        return top_action.force_type if top_action else None

    @property
    def v2_to(self):
        return f'/trr/{self.id}/'
