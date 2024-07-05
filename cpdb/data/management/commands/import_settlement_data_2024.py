import logging
from csv import DictReader
# import sys
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
# from datetime import date
from tqdm import tqdm
from data.models import Officer
from lawsuit.models import Lawsuit
from datetime import datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--table_name', help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        table_name = kwargs.get('table_name')

        if not table_name:
            logger.error("Please provide a valid file path.")
            return

        with transaction.atomic():
            with connection.constraint_checks_disabled():
                # cursor = connection.cursor()
                print("Deleting previous objects")
                Lawsuit.objects.all().delete()

                cursor = connection.cursor()
                cursor.execute("SELECT * FROM " + table_name)
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))
                    if row['uid'].strip() != '':
                        id = row['uid'].split('.')
                        officer1 = Officer.objects.get(pk=int(id[0]))

                    try:
                        lawsuit = Lawsuit.objects.get(case_no=row['case_id'].strip())

                    except Lawsuit.DoesNotExist:
                        logger.warning(f"No officer found for UID: {row['uid']}")
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
                    if row['uid'].strip() != '':
                        lawsuit.officers.add(officer1)
                    lawsuit.save()

        logger.info("Settlements Finished successfully")
