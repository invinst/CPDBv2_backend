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

AREA_CHOICES = [
    ['beat', 'Beat'],
    ['neighborhoods', 'Neighborhood'],
    ['police-beats', 'Police Beat'],
    ['school-grounds', 'School Ground'],
    ['wards', 'Ward'],
    ['Community', 'Community'],
    ['police-districts', 'Police District']
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

CPDB_V1_OFFICER_PATH = 'https://cpdb.co/officer'
