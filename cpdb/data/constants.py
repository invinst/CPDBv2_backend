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

LOCATION_CHOICES = [
    ['01', 'Food Sales/Restaurant'],
    ['02', 'Tavern/Liquor Store'],
    ['03', 'Other Business Establishment'],
    ['04', 'Police Building'],
    ['05', 'Lockup Facility'],
    ['06', 'Police Maintenance Facility'],
    ['07', 'CPD Automotive Pound Facility'],
    ['08', 'Other Police Property'],
    ['09', 'Police Communications System'],
    ['10', 'Court Room'],
    ['11', 'Public Transportation Veh./Facility'],
    ['12', 'Park District Property'],
    ['13', 'Airport'],
    ['14', 'Public Property - Other'],
    ['15', 'Other Private Premise'],
    ['16', 'Expressway/Interstate System'],
    ['17', 'Public Way - Other'],
    ['18', 'Waterway. Incl Park District'],
    ['19', 'Private Residence']
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

OUTCOMES = [
    ['000', 'Violation Noted'],
    ['001', '1 Day Suspension'],
    ['002', '2 Day Suspension'],
    ['003', '3 Day Suspension'],
    ['004', '4 Day Suspension'],
    ['005', '5 Day Suspension'],
    ['006', '6 Day Suspension'],
    ['007', '7 Day Suspension'],
    ['008', '8 Day Suspension'],
    ['009', '9 Day Suspension'],
    ['010', '10 Day Suspension'],
    ['011', '11 Day Suspension'],
    ['012', '12 Day Suspension'],
    ['013', '13 Day Suspension'],
    ['014', '14 Day Suspension'],
    ['015', '15 Day Suspension'],
    ['016', '16 Day Suspension'],
    ['017', '17 Day Suspension'],
    ['018', '18 Day Suspension'],
    ['019', '19 Day Suspension'],
    ['020', '20 Day Suspension'],
    ['021', '21 Day Suspension'],
    ['022', '22 Day Suspension'],
    ['023', '23 Day Suspension'],
    ['024', '24 Day Suspension'],
    ['025', '25 Day Suspension'],
    ['026', '26 Day Suspension'],
    ['027', '27 Day Suspension'],
    ['028', '28 Day Suspension'],
    ['029', '29 Day Suspension'],
    ['030', '30 Day Suspension'],
    ['045', '45 Day Suspension'],
    ['060', '60 Day Suspension'],
    ['090', '90 Day Suspension'],
    ['100', 'Reprimand'],
    ['120', 'Suspended for 120 Days'],
    ['180', 'Suspended for 180 Days'],
    ['200', 'Suspended over 30 Days'],
    ['300', 'Administrative Termination'],
    ['400', 'Separation'],
    ['500', 'Reinstated by Police Board'],
    ['600', 'No Action Taken'],
    ['700', 'Reinstated by Court Action'],
    ['800', 'Resigned'],
    ['900', 'Penalty Not Served'],
    ['', 'Unknown'],
]

NO_DISCIPLINE_CODES = ('600', '000', '500', '700', '800', '900', '')
DISCIPLINE_CODES = [
    x[0] for x in OUTCOMES
    if x[0] not in NO_DISCIPLINE_CODES and x[0] is not None]

OUTCOMES_DICT = dict(OUTCOMES)

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

PERCENTILE_ALLEGATION = 'metric_allegation'
PERCENTILE_ALLEGATION_INTERNAL = 'metric_allegation_internal'
PERCENTILE_ALLEGATION_CIVILIAN = 'metric_allegation_civilian'
PERCENTILE_TRR = 'metric_trr'
PERCENTILE_TYPES = [
    PERCENTILE_ALLEGATION,
    PERCENTILE_ALLEGATION_INTERNAL,
    PERCENTILE_ALLEGATION_CIVILIAN,
    PERCENTILE_TRR
]
