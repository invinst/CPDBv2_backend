import logging
from csv import DictReader
import csv
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
# from datetime import date
from tqdm import tqdm
# from data.models import Officer, PoliceUnit
from trr.models import TRR, TRRStatus
from datetime import datetime
# from django.contrib.gis.geos import Point
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

        with open(file_path) as f, open('error_statuses.csv', 'w', newline='') as error_file:
            reader = DictReader(f)

            fieldnames = reader.fieldnames
            error_writer = csv.DictWriter(error_file, fieldnames=fieldnames)
            error_writer.writeheader()
            # tag = ''
            eastern = pytz.utc

            with transaction.atomic():
                with connection.constraint_checks_disabled():
                    # cursor = connection.cursor()

                    for row in tqdm(reader, desc='Updating TRR Statuses'):
                        if row['trr_id'] != '':
                            try:
                                trr = TRR.objects.get(pk=row['trr_id'].replace("-", ""))
                                status = TRRStatus(
                                    trr=trr,
                                    # officer=officer,
                                    rank=row['rank'],
                                    star=row['star'],
                                    status=row['status'],
                                    age=row['age'].split('.')[0] if row['age'] != '' else None,
                                )
                                try:
                                    dt = datetime.strptime(row['status_date'] + " " + row['status_time'],
                                                           '%Y-%m-%d %H:%M:%S')
                                    localized_dt = eastern.localize(dt)
                                    status.status_datetime = localized_dt
                                except pytz.AmbiguousTimeError:
                                    print("Except")
                                    # trr.incident_date = incident_value

                                status.save()
                            except TRR.DoesNotExist:
                                error_writer.writerow(row)
                                print(row)

        logger.info("Finished successfully")
