import logging
from csv import DictReader
# import sys
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from datetime import date
from tqdm import tqdm
from data.models import Officer
from lawsuit.models import Lawsuit
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
                    Lawsuit.objects.all().delete()

                    for row in tqdm(reader, desc='Updating Settlements'):
                        if row['UID'].strip() != '':
                            id = row['UID'].split('.')
                            officer1 = Officer.objects.get(pk=int(id[0]))

                        try:
                            lawsuit = Lawsuit.objects.get(case_no=row['case_id'].strip())

                        except Lawsuit.DoesNotExist:
                            logger.warning(f"No officer found for UID: {row['UID']}")
                            lawsuit = Lawsuit()

                        lawsuit.case_no = row['case_id'].strip()
                        lawsuit.add2 = row['address'].strip()
                        lawsuit.incident_date = datetime.strptime(row['incident_date'], '%Y-%m-%d') if row[
                            'incident_date'].strip() else None
                        lawsuit.summary = row['narrative']
                        lawsuit.requester_full_name = row['complaint']
                        lawsuit.location = row['location']
                        lawsuit.primary_cause = row['complaint']
                        lawsuit.total_settlement = row['settlement'].replace('$', '').replace(',', '')
                        lawsuit.total_payments = row['settlement'].replace('$', '').replace(',', '')
                        lawsuit.save()
                        if row['UID'].strip() != '':
                            lawsuit.officers.add(officer1)
                        lawsuit.save()

        logger.info("Settlements Finished successfully")
