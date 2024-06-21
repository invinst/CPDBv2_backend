import logging
from csv import DictReader
import csv
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
# from datetime import date
from tqdm import tqdm
from data.models import Allegation, Investigator, InvestigatorAllegation, PoliceUnit
from datetime import datetime
# from django.contrib.gis.geos import Point
# import pytz

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file_path', help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs.get('file_path')

        if not file_path:
            logger.error("Please provide a valid file path.")
            return

        with open(file_path) as f, open('error_investigators.csv', 'w', newline='') as error_file:
            reader = DictReader(f)

            fieldnames = reader.fieldnames
            error_writer = csv.DictWriter(error_file, fieldnames=fieldnames)
            error_writer.writeheader()
            # tag = ''
            # eastern = pytz.utc

            with transaction.atomic():
                Investigator.objects.all().delete()
                with connection.constraint_checks_disabled():
                    # cursor = connection.cursor()
                    for row in tqdm(reader, desc='Updating Investigators'):
                        investigator = Investigator(
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            middle_initial=row['middle_initial'],
                            suffix_name=row['suffix_name'],
                            appointed_date=datetime.strptime(row['appointed_date'], '%Y-%m-%d') if row[
                                'appointed_date'].strip() else None
                        )
                        investigator.save()

                        investigator_allegation = InvestigatorAllegation(
                            investigator=investigator,
                            current_star=row['current_star'],
                            current_rank=row['current_rank'],

                        )
                        if row['current_unit'] != '':
                            unit = row['current_unit'].split('.')
                            policy_unit = PoliceUnit.objects.filter(
                                unit_name=unit[0].zfill(3)
                            )
                            if len(policy_unit) > 0:
                                investigator_allegation.current_unit = policy_unit[0]

                        try:
                            allegation = Allegation.objects.get(crid=row['cr_id'].replace("-", ""))
                            investigator_allegation.allegation = allegation
                        except Allegation.DoesNotExist:
                            print(row)
                            error_writer.writerow(row)
                            continue

                        investigator_allegation.save()

        logger.info("Investigators Finished successfully")
