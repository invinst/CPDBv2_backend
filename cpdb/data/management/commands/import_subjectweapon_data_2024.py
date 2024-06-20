import logging
from csv import DictReader
import csv
from django.core.management import BaseCommand
from django.db import DatabaseError, transaction
from django.db import connection
from datetime import date
from tqdm import tqdm
from data.models import Officer, PoliceUnit
from trr.models import TRR, SubjectWeapon
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

        with open(file_path) as f, open('error_subject_weapon.csv', 'w', newline='') as error_file:
            reader = DictReader(f)

            fieldnames = reader.fieldnames
            error_writer = csv.DictWriter(error_file, fieldnames=fieldnames)
            error_writer.writeheader()
            tag = ''
            eastern = pytz.utc

            with transaction.atomic():
                with connection.constraint_checks_disabled():
                    cursor = connection.cursor()

                    for row in tqdm(reader, desc='Updating TRR Subject Weapon'):
                        if row['trr_id'] != '':
                            try:
                                trr = TRR.objects.get(pk=row['trr_id'].replace("-", ""))

                                weapon = SubjectWeapon(
                                    trr=trr,
                                    weapon_type=row['weapon_type'],
                                    firearm_caliber=row['firearm_caliber'],
                                    weapon_description=row['weapon_description'] if len(row['weapon_description']) < 150 else None,
                                )

                                weapon.save()
                            except TRR.DoesNotExist:
                                error_writer.writerow(row)
                                print(row)
                                continue


        logger.info("Finished successfully")
