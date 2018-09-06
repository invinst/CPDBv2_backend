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
    (WC_OTHER, 'Other'),
    (WC_CLEAR, 'Clear'),
    (WC_SNOW, 'Snow'),
    (WC_RAIN, 'Rain'),
    (WC_SLEET_HAIL, 'Sleet/hail'),
    (WC_SEVERE_CROSS_WIND, 'Severe Cross Wind'),
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

AP_MEMBER_ACTION = 'Member Action'
AP_SUBJECT_ACTION = 'Subject Action'

ACTION_PERSON_CHOICES = (
    (AP_MEMBER_ACTION, 'Member Action'),
    (AP_SUBJECT_ACTION, 'Subject Action')
)

RT_ACTIVE_RESISTER = 'Active Resister'
RT_PASSIVE_RESISTER = 'Passive Resister'
RT_ASSAILAINT_BATTERY = 'Assailant Battery'
RT_ASSAILAINT_ASSAULT_BATTERY = 'Assailant Assault/Battery'
RT_ASSAILAINT_ASSAULT = 'Assailant Assault'
RT_ASSAILAINT_DEADLY_FORCE = 'Assailant Deadly Force'

RESISTANCE_TYPE_CHOICES = (
    (RT_ACTIVE_RESISTER, 'Active Resister'),
    (RT_PASSIVE_RESISTER, 'Passive Resister'),
    (RT_ASSAILAINT_BATTERY, 'Assailant Battery'),
    (RT_ASSAILAINT_ASSAULT_BATTERY, 'Assailant Assault/Battery'),
    (RT_ASSAILAINT_ASSAULT, 'Assailant Assault'),
    (RT_ASSAILAINT_DEADLY_FORCE, 'Assailant Deadly Force')
)

RL_ACTIVE = 'Active'
RL_PASSIVE = 'Passive'
RL_ASSAULT_BATTERY = 'Assault/Battery'
RL_DEADLY_FORCE = 'Deadly Force'

RESISTANCE_LEVEL_CHOICES = (
    (RL_ACTIVE, 'Active'),
    (RL_PASSIVE, 'Passive'),
    (RL_ASSAULT_BATTERY, 'Assault/Battery'),
    (RL_DEADLY_FORCE, 'Deadly Force')
)

HWT_RIGHT_SIDE = 'RIGHT SIDE (WAIST)'
HWT_OTHER = 'OTHER (SPECIFY)'
HWT_LEFT_SIDE = 'LEFT SIDE (WAIST)'

HANDGUN_WORN_TYPE_CHOICES = (
    (HWT_RIGHT_SIDE, 'Right Side (Waist)'),
    (HWT_OTHER, 'Other (Specify)'),
    (HWT_LEFT_SIDE, 'Left Side (Waist)')
)

HDT_STRONG_SIDE = 'STRONG SIDE DRAW'
HDT_CROSS_DRAW = 'CROSS DRAW'
HDT_OTHER = 'OTHER (SPECIFY)'

HANDGUN_DRAWN_TYPE_CHOICES = (
    (HDT_STRONG_SIDE, 'Strong Side Draw'),
    (HDT_CROSS_DRAW, 'Cross Draw'),
    (HDT_OTHER, 'Other (Specify)')
)

OSD_OBJECT = 'OBJECT'
OSD_PERSON = 'PERSON'
OSD_UNKNOWN = 'UNKNOWN'
OSD_BOTH = 'BOTH'

OBJECT_STRUCK_OF_DISCHARGE_CHOICES = (
    (OSD_OBJECT, 'OBJECT'),
    (OSD_PERSON, 'PERSON'),
    (OSD_UNKNOWN, 'UNKNOWN'),
    (OSD_BOTH, 'BOTH')
)

DS_STANDING = 'STANDING'
DS_SITTING = 'SITTING'
DS_OTHER = 'OTHER (SPECIFY)'
DS_KNEELING = 'KNEELING'
DS_LYING_DOWN = 'LYING DOWN'

DISCHARGE_POSITION_CHOICES = (
    (DS_STANDING, 'Standing'),
    (DS_SITTING, 'Sitting'),
    (DS_OTHER, 'Other (Specify)'),
    (DS_KNEELING, 'Kneeling'),
    (DS_LYING_DOWN, 'Lying Down')
)

S_SUBMITTED = 'SUBMITTED'
S_REVIEWED = 'REVIEWED'
S_APPROVED = 'APPROVED'

TRR_STATUS_CHOICES = (
    (S_SUBMITTED, 'SUBMITTED'),
    (S_REVIEWED, 'REVIEWED'),
    (S_APPROVED, 'APPROVED')
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
    officer = models.ForeignKey('data.Officer', null=True)
    officer_assigned_beat = models.CharField(max_length=16, null=True)
    officer_unit = models.ForeignKey('data.PoliceUnit', null=True)
    officer_unit_detail = models.ForeignKey('data.PoliceUnit', null=True, related_name='trr_unit_detail_reverse')
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
        return '/trr/%s/' % self.id


class ActionResponse(models.Model):
    trr = models.ForeignKey(TRR)
    person = models.CharField(max_length=16, null=True, choices=ACTION_PERSON_CHOICES)
    resistance_type = models.CharField(max_length=32, null=True, choices=RESISTANCE_TYPE_CHOICES)
    action = models.CharField(max_length=64, null=True)
    other_description = models.CharField(max_length=64, null=True)
    member_action = models.CharField(max_length=64, null=True)
    force_type = models.CharField(max_length=64, null=True)
    action_sub_category = models.CharField(max_length=3, null=True)
    action_category = models.CharField(max_length=1, null=True)
    resistance_level = models.CharField(max_length=16, null=True, choices=RESISTANCE_LEVEL_CHOICES)


class WeaponDischarge(models.Model):
    trr = models.ForeignKey(TRR)
    weapon_type = models.CharField(max_length=32, null=True)
    weapon_type_description = models.CharField(max_length=32, null=True)
    firearm_make = models.CharField(max_length=64, null=True)
    firearm_model = models.CharField(max_length=32, null=True)
    firearm_barrel_length = models.CharField(max_length=16, null=True)
    firearm_caliber = models.CharField(max_length=16, null=True)
    total_number_of_shots = models.SmallIntegerField(null=True)
    firearm_reloaded = models.NullBooleanField()
    number_of_catdridge_reloaded = models.SmallIntegerField(null=True)
    handgun_worn_type = models.CharField(max_length=32, null=True, choices=HANDGUN_WORN_TYPE_CHOICES)
    handgun_drawn_type = models.CharField(max_length=32, null=True, choices=HANDGUN_DRAWN_TYPE_CHOICES)
    method_used_to_reload = models.CharField(max_length=64, null=True)
    sight_used = models.NullBooleanField()
    protective_cover_used = models.CharField(max_length=32, null=True)
    discharge_distance = models.CharField(max_length=16, null=True)
    object_struck_of_discharge = models.CharField(max_length=32, null=True, choices=OBJECT_STRUCK_OF_DISCHARGE_CHOICES)
    discharge_position = models.CharField(max_length=32, null=True, choices=DISCHARGE_POSITION_CHOICES)


class Charge(models.Model):
    trr = models.ForeignKey(TRR)
    sr_no = models.PositiveIntegerField(null=True)
    statute = models.CharField(max_length=64, null=True)
    description = models.CharField(max_length=64, null=True)
    subject_no = models.PositiveIntegerField(null=True)


class TRRStatus(models.Model):
    trr = models.ForeignKey(TRR)
    officer = models.ForeignKey('data.officer', null=True)
    rank = models.CharField(max_length=16, null=True)
    star = models.CharField(max_length=10, null=True)
    status = models.CharField(max_length=16, null=True, choices=TRR_STATUS_CHOICES)
    status_datetime = models.DateTimeField(null=True)
    age = models.SmallIntegerField(null=True)


class SubjectWeapon(models.Model):
    trr = models.ForeignKey(TRR)
    weapon_type = models.CharField(max_length=64, null=True)
    firearm_caliber = models.CharField(max_length=16, null=True)
    weapon_description = models.CharField(max_length=64, null=True)


class TRRAttachmentRequest(models.Model):
    trr = models.ForeignKey(TRR)
    email = models.EmailField(max_length=255)
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = (('trr', 'email'),)

    def __unicode__(self):
        return '%s - %s' % (self.email, self.trr.id)
