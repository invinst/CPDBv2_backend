import csv

from django.core.management import BaseCommand

from data.models import (
    PoliceUnit,
    Officer,
    OfficerBadgeNumber,
    OfficerHistory,
    Area,
    LineArea,
    Investigator,
    Allegation,
    AllegationCategory,
    OfficerAllegation,
    PoliceWitness,
    Complainant,
    Involvement,
    AttachmentFile
)

EXPORT_MODELS = (
    (PoliceUnit, ('pk', 'unit_name'), 'policeunit.csv'),
    (Officer,
     ('pk', 'first_name', 'last_name', 'gender', 'race', 'appointed_date', 'rank', 'birth_year', 'active'),
     'officer.csv'),
    (OfficerBadgeNumber,
     ('pk', 'officer', 'star', 'current'), 'officerbadgenumber.csv'),
    (OfficerHistory,
     ('pk', 'officer', 'unit', 'effective_date', 'end_date'), 'officerhistory.csv'),
    (Area, ('pk', 'name', 'area_type', 'polygon'), 'area.csv'),
    (LineArea, ('pk', 'name', 'linearea_type', 'geom'), 'linearea.csv'),
    (Investigator, (
        'pk', 'raw_name', 'name', 'current_rank', 'unit'), 'investigator.csv'),
    (Allegation, (
        'pk', 'crid', 'summary',
        'location', 'add1', 'add2', 'city',
        'incident_date', 'investigator', 'areas',
        'line_areas', 'point', 'beat', 'source'), 'allegation.csv'),
    (AllegationCategory, (
        'pk', 'category_code', 'category', 'allegation_name',
        'on_duty', 'citizen_dept'), 'allegationcategory.csv'),
    (OfficerAllegation, (
        'pk', 'allegation', 'allegation_category', 'officer',
        'start_date', 'end_date', 'officer_age',
        'recc_finding', 'recc_outcome', 'final_finding', 'final_outcome',
        'final_outcome_class'
        ), 'officerallegation.csv'),
    (PoliceWitness, ('pk', 'allegation', 'gender', 'race', 'officer'), 'policewitness.csv'),
    (Complainant, ('pk', 'allegation', 'gender', 'race', 'age'), 'complainant.csv'),
    (Involvement, (
        'pk', 'allegation', 'officer', 'full_name', 'involved_type', 'gender', 'race', 'age'
        ), 'involvement.csv'),
    (AttachmentFile, (
        'pk', 'file_type', 'title', 'url', 'additional_info', 'tag', 'original_url', 'allegation'
        ), 'attachmentfile.csv')
    )


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model, fieldnames, file_name in EXPORT_MODELS:
            self.print_data(fieldnames, model, file_name)

    def print_data(self, fieldnames, model, file_name):
        rows = model.objects.all().values(*fieldnames)
        with open(file_name, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
