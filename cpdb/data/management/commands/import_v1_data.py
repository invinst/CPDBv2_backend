import sys
import csv
import os

import iso8601
import pytz

from django.core.management import BaseCommand
from django.utils import timezone

from data.models import (
    PoliceUnit, Officer, OfficerBadgeNumber, OfficerHistory, Area, LineArea,
    Investigator, Allegation, AllegationCategory, OfficerAllegation, PoliceWitness,
    Complainant, OfficerAlias)


csv.field_size_limit(sys.maxsize)


IMPORT_MODELS = (
    (PoliceUnit, 'policeunit.csv', None),
    (Officer, 'officer.csv', {
        'officer_first': 'first_name',
        'officer_last': 'last_name',
        'appt_date': 'appointed_date'
        }),
    (OfficerBadgeNumber, 'officerbadgenumber.csv', None),
    (OfficerHistory, 'officerhistory.csv', None),
    (Area, 'area.csv', None),
    (LineArea, 'linearea.csv', None),
    (Investigator, 'investigator.csv', None),
    (Allegation, 'allegation.csv', None),
    (AllegationCategory, 'allegationcategory.csv', None),
    (OfficerAllegation, 'officerallegation.csv', None),
    (PoliceWitness, 'policewitness.csv', None),
    (Complainant, 'complainant.csv', None),
    (OfficerAlias, 'officeralias.csv', None),
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--folder')

    def handle(self, *args, **options):
        for model, file_name, rename in IMPORT_MODELS:
            file_path = os.path.join(options['folder'], file_name)
            self.import_model(model, file_path, rename)

    def str_to_bool(self, str):
        if str == 'True':
            return True
        elif str == 'False':
            return False
        else:
            raise ValueError

    def import_model(self, model, file_name, rename):
        with open(file_name, 'rb') as csv_file:
            reader = csv.reader(csv_file)
            field_names = reader.next()

            # rename field names if necessary
            if rename:
                field_names = [
                    rename[val] if val in rename else val
                    for val in field_names]

            # figure out if any field is a relation
            relation = {
                field_name: model._meta.get_field(field_name).related_model
                for field_name in field_names
                if field_name != 'pk' and model._meta.get_field(field_name).related_model
            }

            # note the many to many fields
            many_to_many = [
                ind for ind in range(len(field_names))
                if field_names[ind] != 'pk' and
                model._meta.get_field(field_names[ind]).many_to_many
            ]

            existing_pks = model.objects.all().values_list('pk', flat=True)

            for row in reader:
                # set row value to None for any nullable field
                row = [
                    None if field_names[ind] != 'pk' and
                    model._meta.get_field(field_names[ind]).null and not
                    row[ind] else row[ind]
                    for ind in range(len(field_names))
                ]

                # make timezone aware any datetime field
                row = [
                    iso8601.parse_date(row[ind])
                    .replace(tzinfo=timezone.get_default_timezone()).astimezone(pytz.utc)
                    if field_names[ind] != 'pk' and row[ind] and
                    model._meta.get_field(field_names[ind]).get_internal_type()
                    in ['DateTimeField']
                    else row[ind]
                    for ind in range(len(field_names))
                ]

                # set row boolean value
                row = [
                    self.str_to_bool(row[ind])
                    if field_names[ind] != 'pk' and
                    model._meta.get_field(field_names[ind]).get_internal_type() == 'BooleanField'
                    else row[ind]
                    for ind in range(len(field_names))
                ]

                # set row value to a related model if necessary
                if relation:
                    row = [
                        relation[field_names[ind]].objects.get(pk=int(row[ind]))
                        if field_names[ind] in relation and row[ind] else row[ind]
                        for ind in range(len(field_names))
                    ]

                # save this row
                value_dict = {
                    field_names[ind]: row[ind]
                    for ind in range(len(field_names))
                    if ind not in many_to_many
                }
                if int(value_dict['pk']) not in existing_pks:
                    # create the model before saving many to many fields
                    if many_to_many:
                        try:
                            obj = model.objects.get(pk=int(value_dict['pk']))
                        except model.DoesNotExist:
                            obj = model.objects.create(**value_dict)
                        for ind in many_to_many:
                            if row[ind]:
                                getattr(obj, field_names[ind]).add(row[ind])
                    else:
                        model.objects.create(**value_dict)
