import logging
from csv import DictReader
import csv
from django.core.management import BaseCommand
from django.db import DatabaseError, transaction
from django.db import connection
from datetime import date
from tqdm import tqdm
from data.models import Officer, Allegation, Victim
from datetime import datetime
from django.contrib.gis.geos import Point
import pytz

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file_path', help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs.get('file_path')

        if not file_path:
            logger.error("Please provide a valid file path.")
            return

        with open(file_path) as f, open('error_victims.csv', 'w', newline='') as error_file:
            reader = DictReader(f)

            fieldnames = reader.fieldnames
            error_writer = csv.DictWriter(error_file, fieldnames=fieldnames)
            error_writer.writeheader()
            tag = ''
            eastern = pytz.utc

            with transaction.atomic():
                Victim.objects.all().delete()
                with connection.constraint_checks_disabled():
                    cursor = connection.cursor()
                    cursor.execute('ALTER TABLE public.data_victim DISABLE TRIGGER ALL;')
                    cursor.execute('ALTER TABLE public.data_victim ALTER COLUMN allegation_id DROP NOT NULL;')
                    for row in tqdm(reader, desc='Updating officer allegations'):
                        print(row)

                        victim = Victim(
                            created_at=date.today(),
                            gender=row['gender'].strip()[0] if row['gender'].strip() != '' else '',
                            race=row['race'].strip(),
                            age=row['age'].split('.')[0] if row['age'].strip() != '' else None,
                            birth_year=row['birth_year'].split('.')[0] if row['birth_year'].strip() != '' else None
                        )

                        try:
                            allegation = Allegation.objects.get(crid=row['cr_id'].replace("-", ""))
                            victim.allegation = allegation
                        except Allegation.DoesNotExist:
                            error_writer.writerow(row)
                            print(row)
                            continue

                        victim.save()

                    cursor.execute('ALTER TABLE public.data_victim ALTER COLUMN allegation_id SET NOT NULL;')
                    cursor.execute('ALTER TABLE public.data_victim ENABLE TRIGGER ALL;')


        logger.info("Finished successfully")
