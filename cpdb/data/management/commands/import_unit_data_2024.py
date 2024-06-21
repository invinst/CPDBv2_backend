import logging
from csv import DictReader
import sys
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
# from datetime import date
from tqdm import tqdm
from data.models import OfficerHistory, Officer, PoliceUnit
from datetime import datetime


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file_path', help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs.get('file_path')

        if not file_path:
            logger.error("Please provide a valid file path.")
            return

        with open(file_path) as f:
            reader = DictReader(f)
            # tag = ''
            with transaction.atomic():
                with connection.constraint_checks_disabled():
                    # cursor = connection.cursor()
                    print("Deleting previous objects")
                    OfficerHistory.objects.all().delete()

                    for row in tqdm(reader, desc='Updating Units'):
                        id = row['UID'].split('.')
                        officer1 = Officer.objects.get(pk=int(id[0]))

                        policy_unit = PoliceUnit.objects.filter(
                            unit_name=row['unit'].zfill(3)
                        )

                        officer_history = OfficerHistory(
                            effective_date=datetime.strptime(row['unit_start_date'], '%Y-%m-%d') if row[
                                'unit_start_date'].strip() else None,
                            end_date=datetime.strptime(row['unit_end_date'], '%Y-%m-%d') if row[
                                'unit_end_date'].strip() else None,
                            officer=officer1,
                            unit=policy_unit[0] if len(policy_unit) > 0 else None
                        )
                        officer_history.save()

        logger.info("Finished successfully")
