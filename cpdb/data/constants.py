from datetime import datetime

from django.conf import settings

import pytz


ACTIVE_YES_CHOICE = 'Yes'
ACTIVE_NO_CHOICE = 'No'
ACTIVE_UNKNOWN_CHOICE = 'Unknown'
ACTIVE_CHOICES = [
    [ACTIVE_YES_CHOICE, 'Active'],
    [ACTIVE_NO_CHOICE, 'Inactive'],
    [ACTIVE_UNKNOWN_CHOICE, 'Unknown']
]

CITIZEN_CHOICE = 'citizen'
DEPT_CHOICE = 'dept'
UNKNOWN_CHOICE = '?'
CITIZEN_DEPTS = [
    (CITIZEN_CHOICE, 'Citizen'),
    (DEPT_CHOICE, 'Dept'),
    (UNKNOWN_CHOICE, 'Unknown')
]


BEAT_AREA_CHOICE = 'beat'
NEIGHBORHOODS_AREA_CHOICE = 'neighborhoods'
POLICE_BEATS_AREA_CHOICE = 'police-beats'
SCHOOL_GROUNDS_AREA_CHOICE = 'school-grounds'
WARDS_AREA_CHOICE = 'wards'
COMMUNITY_AREA_CHOICE = 'community'
POLICE_DISTRICTS_AREA_CHOICE = 'police-districts'
AREA_CHOICES = [
    [BEAT_AREA_CHOICE, 'Beat'],
    [NEIGHBORHOODS_AREA_CHOICE, 'Neighborhood'],
    [POLICE_BEATS_AREA_CHOICE, 'Police Beat'],
    [SCHOOL_GROUNDS_AREA_CHOICE, 'School Ground'],
    [WARDS_AREA_CHOICE, 'Ward'],
    [COMMUNITY_AREA_CHOICE, 'Community'],
    [POLICE_DISTRICTS_AREA_CHOICE, 'Police District']
]

LINE_AREA_CHOICES = [['passageway', 'Passageway']]

AGENCY_CHOICES = [['IPRA', 'IPRA'], ['IAD', 'IAD']]

FINDINGS = [
    ['UN', 'Unfounded'],  # means final_outcome_class = not-sustained
    ['EX', 'Exonerated'],  # means final_outcome_class = not-sustained
    ['NS', 'Not Sustained'],  # means final_outcome_class = not-sustained
    ['SU', 'Sustained'],  # means final_outcome_class = sustained
    ['NC', 'No Cooperation'],  # means final_outcome_class = not-sustained
    ['NA', 'No Affidavit'],  # means final_outcome_class = not-sustained
    ['DS', 'Discharged'],  # means final_outcome_class = not-sustained
    ['ZZ', 'Unknown']  # means final_outcome_class = open-investigation
]

FINDINGS_DICT = dict(FINDINGS)

CPDB_V1_OFFICER_PATH = 'https://cpdb.co/officer'

GENDER = [
    ['M', 'Male'],
    ['F', 'Female'],
    ['X', 'X']
]

GENDER_DICT = dict(GENDER)

MEDIA_TYPE_VIDEO = 'video'
MEDIA_TYPE_AUDIO = 'audio'
MEDIA_TYPE_DOCUMENT = 'document'

MEDIA_TYPE_CHOICES = [
    [MEDIA_TYPE_VIDEO, 'Video'],
    [MEDIA_TYPE_AUDIO, 'Audio'],
    [MEDIA_TYPE_DOCUMENT, 'Document']
]

MEDIA_IPRA_COPA_HIDING_TAGS = ['OCIR', 'AR']
MEDIA_HIDING_TITLES = ['arrest report']

BACKGROUND_COLOR_SCHEME = {
    '00': '#f5f4f4',
    '10': '#edf0fa',
    '01': '#f8eded',
    '20': '#d4e2f4',
    '11': '#ecdeef',
    '02': '#efdede',
    '30': '#c6d4ec',
    '21': '#d9d1ee',
    '12': '#eacbe0',
    '03': '#ebcfcf',
    '40': '#aec9e8',
    '31': '#c0c3e1',
    '22': '#cdbddd',
    '13': '#e4b8cf',
    '04': '#f0b8b8',
    '50': '#90b1f5',
    '41': '#aaace3',
    '32': '#b6a5de',
    '23': '#c99edc',
    '14': '#e498b6',
    '05': '#f89090',
    '51': '#748be4',
    '42': '#8e84e0',
    '33': '#af7fbd',
    '24': '#c873a2',
    '15': '#e1718a',
    '52': '#6660ae',
    '43': '#8458aa',
    '34': '#a34e99',
    '25': '#b5496a',
    '53': '#4c3d8f',
    '44': '#6b2e7e',
    '35': '#792f55',
    '54': '#391c6a',
    '45': '#520051',
    '55': '#131313',
}

RACE_UNKNOWN_STRINGS = ['nan', '']


PERCENTILE_ALLEGATION_GROUP = 'PERCENTILE_ALLEGATION_GROUP'
PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP = 'PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP'
PERCENTILE_TRR_GROUP = 'PERCENTILE_TRR_GROUP'
PERCENTILE_HONORABLE_MENTION_GROUP = 'PERCENTILE_HONORABLE_MENTION_GROUP'
PERCENTILE_GROUPS = [
    PERCENTILE_ALLEGATION_GROUP,
    PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP,
    PERCENTILE_TRR_GROUP,
    PERCENTILE_HONORABLE_MENTION_GROUP
]

MAJOR_AWARDS = [
    'honored police star',
    'carter harrison',
    'lambert tree medal',
    'lambert tree',
    'richard j. daley police medal of honor',
    'police medal',
    'superintendents award of valor',
    "superintendent's award of valor",
    '100 club of chicago valor award',
    'hundred club of cook county medal of valor',
    'superintendents award of merit',
    "superintendent's award of merit",
]


ALLEGATION_MIN_DATETIME = datetime.strptime(settings.ALLEGATION_MIN, '%Y-%m-%d').replace(tzinfo=pytz.utc)
ALLEGATION_MAX_DATETIME = datetime.strptime(settings.ALLEGATION_MAX, '%Y-%m-%d').replace(tzinfo=pytz.utc)

<<<<<<< HEAD
HEATMAP_END_YEAR = 2018
=======
HEATMAP_END_YEAR = 2023
>>>>>>> staging

INTERNAL_CIVILIAN_ALLEGATION_MIN_DATETIME = datetime.strptime(
    settings.INTERNAL_CIVILIAN_ALLEGATION_MIN, '%Y-%m-%d'
).replace(tzinfo=pytz.utc)
INTERNAL_CIVILIAN_ALLEGATION_MAX_DATETIME = datetime.strptime(
    settings.INTERNAL_CIVILIAN_ALLEGATION_MAX, '%Y-%m-%d'
).replace(tzinfo=pytz.utc)

TRR_MIN_DATETIME = datetime.strptime(settings.TRR_MIN, '%Y-%m-%d').replace(tzinfo=pytz.utc)
TRR_MAX_DATETIME = datetime.strptime(settings.TRR_MAX, '%Y-%m-%d').replace(tzinfo=pytz.utc)

MIN_VISUAL_TOKEN_YEAR = min(INTERNAL_CIVILIAN_ALLEGATION_MIN_DATETIME.year, TRR_MIN_DATETIME.year)
MAX_VISUAL_TOKEN_YEAR = max(INTERNAL_CIVILIAN_ALLEGATION_MAX_DATETIME.year, TRR_MAX_DATETIME.year)


class AttachmentSourceType(object):
    PORTAL_COPA = 'PORTAL_COPA'
    SUMMARY_REPORTS_COPA = 'SUMMARY_REPORTS_COPA'
    DOCUMENTCLOUD = 'DOCUMENTCLOUD'
    PORTAL_COPA_DOCUMENTCLOUD = 'PORTAL_COPA_DOCUMENTCLOUD'
    SUMMARY_REPORTS_COPA_DOCUMENTCLOUD = 'SUMMARY_REPORTS_COPA_DOCUMENTCLOUD'

    DOCUMENTCLOUD_SOURCE_TYPES = [
        DOCUMENTCLOUD,
        PORTAL_COPA_DOCUMENTCLOUD,
        SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
    ]

    COPA_DOCUMENTCLOUD_SOURCE_TYPES = [
        PORTAL_COPA_DOCUMENTCLOUD,
        SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
    ]

    SOURCE_TYPE_MAPPINGS = {
        PORTAL_COPA: PORTAL_COPA_DOCUMENTCLOUD,
        SUMMARY_REPORTS_COPA: SUMMARY_REPORTS_COPA_DOCUMENTCLOUD
    }


UPLOAD_FAIL_MAX_ATTEMPTS = 5
