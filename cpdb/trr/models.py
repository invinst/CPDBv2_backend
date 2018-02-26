from django.contrib.gis.db import models

from data.constants import GENDER


DIRECTION_WEST = 'West'
DIRECTION_NORTH = 'North'
DIRECTION_SOUTH = 'South'
DIRECTION_EAST = 'East'
DIRECTION_CHOICES = (
    (DIRECTION_WEST, 'West'),
    (DIRECTION_NORTH, 'North'),
    (DIRECTION_SOUTH, 'South'),
    (DIRECTION_EAST, 'East')
)

INDOOR = 'Indoor'
OUTDOOR = 'Outdoor'
INDOOR_OUTDOOR_CHOICES = (
    (INDOOR, 'Indoor'),
    (OUTDOOR, 'Outdoor')
)

LC_DAYLIGHT = 'DAYLIGHT'
LC_GOOD_ARTIFICIAL = 'GOOD ARTIFICIAL'
LC_DUSK = 'DUSK'
LC_NIGHT = 'NIGHT'
LC_POOR_ARTIFICIAL = 'POOR ARTIFICIAL'
LC_DAWN = 'DAWN'

LIGHTNING_CONDITION_CHOICES = (
    (LC_DAYLIGHT, 'Daylight'),
    (LC_GOOD_ARTIFICIAL, 'Good Artificial'),
    (LC_DUSK, 'Dusk'),
    (LC_NIGHT, 'Night'),
    (LC_POOR_ARTIFICIAL, 'Poor Artificial'),
    (LC_DAWN, 'Dawn')
)

WC_OTHER = 'OTHER'
WC_CLEAR = 'CLEAR'
WC_SNOW = 'SNOW'
WC_RAIN = 'RAIN'
WC_SLEET_HAIL = 'SLEET/HAIL'
WC_SEVERE_CROSS_WIND = 'SEVERE CROSS WIND'
WC_FOG_SMOKE_HAZE = 'FOG/SMOKE/HAZE'

WEATHER_CONDITION_CHOICES = (
    (WC_OTHER, 'Other')
    (WC_CLEAR, 'Clear')
    (WC_SNOW, 'Snow')
    (WC_RAIN, 'Rain')
    (WC_SLEET_HAIL, 'Sleet/hail')
    (WC_SEVERE_CROSS_WIND, 'Severe Cross Wind')
    (WC_FOG_SMOKE_HAZE, 'Fog/smoke/haze')
)

PFF_MEMBER = 'MEMBER'
PFF_OTHER = 'OTHER'
PFF_OFFENDER = 'OFFENDER'

PARTY_FIRED_FIRST_CHOICES = (
    (PFF_MEMBER, 'Member'),
    (PFF_OTHER, 'Other'),
    (PFF_OFFENDER, 'Offender')
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
    # officer = models.ForeignKey('data.Officer')
    # officer_assigned_beat = models.CharField(max_length=255, null=True)
    # officer_duty_status = models.NullBooleanField()
    # officer_in_uniform = models.NullBooleanField()
    officer_injured = models.NullBooleanField()
    # unit = models.ForeignKey('data.PoliceUnit')
    # unit_detail = models.CharField(max_length=255, null=True)
    subject_id = models.PositiveSmallIntegerField(null=True)
    subject_armed = models.NullBooleanField()
    subject_injured = models.NullBooleanField()
    subject_alleged_injury = models.NullBooleanField()
    subject_age = models.PositiveSmallIntegerField(null=True)
    subject_birth_year = models.PositiveSmallIntegerField(null=True)
    subject_gender = models.CharField(max_length=1, null=True, choices=GENDER)
    subject_race = models.CharField(max_length=32, null=True)
