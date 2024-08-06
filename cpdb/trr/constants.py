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
LC_ARTIFICIAL = 'ARTIFICIAL'  # TODO: check that there isn't another column specifying good or poor in new format
LC_ART = 'ART'
LC_DAR = 'DAR'
LC_DAY = 'DAY'
LC_DUSK = 'DUSK'
LC_NIGHT = 'NIGHT'
LC_DARKNESS = 'DARKNESS'
LC_POOR_ARTIFICIAL = 'POOR ARTIFICIAL'
LC_DAWN = 'DAWN'
LIGHTNING_CONDITION_CHOICES = (
    (LC_DAYLIGHT, 'Daylight'),
    (LC_DAY, 'Daylight'),
    (LC_GOOD_ARTIFICIAL, 'Good Artificial'),
    (LC_ARTIFICIAL, 'Artificial'),
    (LC_ART, 'Artificial'),
    (LC_DARKNESS, 'Darkness'),
    (LC_DAR, 'Darkness'),
    (LC_DUSK, 'Dusk'),
    (LC_NIGHT, 'Night'),
    (LC_POOR_ARTIFICIAL, 'Poor Artificial'),
    (LC_DAWN, 'Dawn')
)
WC_OTHER = 'OTHER'
WC_CLEAR = 'CLEAR'
WC_SNOW = 'SNOW'
WC_RAIN = 'RAIN'
WC_CLOUD = 'CLOUD'
WC_SLEET_HAIL = 'SLEET/HAIL'
WC_SEVERE_CROSS_WIND = 'SEVERE CROSS WIND'
WC_FOG_SMOKE_HAZE = 'FOG/SMOKE/HAZE'
WC_FOG = 'FOG'
WEATHER_CONDITION_CHOICES = (
    (WC_OTHER, 'Other'),
    (WC_CLEAR, 'Clear'),
    (WC_SNOW, 'Snow'),
    (WC_RAIN, 'Rain'),
    (WC_CLOUD, 'Cloud'),
    (WC_SLEET_HAIL, 'Sleet/hail'),
    (WC_SEVERE_CROSS_WIND, 'Severe Cross Wind'),
    (WC_FOG_SMOKE_HAZE, 'Fog/smoke/haze'),
    (WC_FOG, 'Fog/smoke/haze')
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
OSD_ANIMAL = 'ANIMAL'
OBJECT_STRUCK_OF_DISCHARGE_CHOICES = (
    (OSD_OBJECT, 'OBJECT'),
    (OSD_PERSON, 'PERSON'),
    (OSD_UNKNOWN, 'UNKNOWN'),
    (OSD_BOTH, 'BOTH'),
    (OSD_ANIMAL, 'ANIMAL')
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
