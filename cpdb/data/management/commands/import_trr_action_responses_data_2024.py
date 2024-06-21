import logging
from csv import DictReader
import csv
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
# from datetime import date
from tqdm import tqdm
# from data.models import Officer, PoliceUnit
from trr.models import TRR, ActionResponse
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

        with open(file_path) as f, open('error_action_responses.csv', 'w', newline='') as error_file:
            reader = DictReader(f)

            fieldnames = reader.fieldnames
            error_writer = csv.DictWriter(error_file, fieldnames=fieldnames)
            error_writer.writeheader()
            # tag = ''
            # eastern = pytz.utc

            with transaction.atomic():
                with connection.constraint_checks_disabled():
                    # cursor = connection.cursor()
                    for row in tqdm(reader, desc='Updating TRR Action Response'):

                        if row['trr_id'] != '':
                            try:
                                trr = TRR.objects.get(pk=row['trr_id'].replace("-", ""))
                                action_response = ActionResponse(
                                    person=row['person'],
                                    resistance_type=row['resistance_type'],
                                    action=row['action'],
                                    other_description=row['other_description'],
                                    member_action=row['member_action'],
                                    force_type=row['force_type'],
                                    action_sub_category=row['action_sub_category'],
                                    action_category=row['action_category'].split('.')[0] if
                                    row['action_category'] != '' else None,
                                    resistance_level=row['resistance_level']
                                )
                                action_response.trr = trr
                                action_response.save()

                            except TRR.DoesNotExist:
                                error_writer.writerow(row)
                                print(row)

        logger.info("Finished successfully")
