import logging
from csv import DictReader
import csv
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from datetime import date
from tqdm import tqdm
from data.models import Allegation, Complainant
# from datetime import datetime
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

        with open(file_path) as f, open('error_complaints.csv', 'w', newline='') as error_file:
            reader = DictReader(f)

            fieldnames = reader.fieldnames
            error_writer = csv.DictWriter(error_file, fieldnames=fieldnames)
            error_writer.writeheader()
            # tag = ''
            # eastern = pytz.utc

            with transaction.atomic():
                with connection.constraint_checks_disabled():
                    # cursor = connection.cursor()
                    Complainant.objects.all().delete()
                    for row in tqdm(reader, desc='Updating complaints'):

                        complaint = Complainant(
                            created_at=date.today(),
                            race=row['race'],
                        )
                        if row['age'] != '':
                            age = row['age'].split('.')
                            complaint.age = age[0]
                        if row['birth_year'] != '':
                            year = row['birth_year'].split('.')
                            complaint.birth_year = year[0] if year[0].isnumeric() else None
                        if row['gender'] != '':
                            complaint.gender = row['gender'][0]

                        try:
                            allegation = Allegation.objects.get(crid=row['cr_id'].replace("-", ""))
                            complaint.allegation = allegation
                        except Allegation.DoesNotExist:
                            error_writer.writerow(row)
                            print(row)

                        #print(row)
                        complaint.save()

        logger.info("Complaints Finished successfully")
