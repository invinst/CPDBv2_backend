import logging
from csv import DictReader
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from tqdm import tqdm
from data.models import Award, Officer
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

                print("Deleting previous objects")
                Award.objects.all().delete()

                cursor = connection.cursor()
                cursor.execute("SELECT * FROM " + table_name)
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))
                    id = row['uid'].split('.')
                    officer1 = Officer.objects.get(pk=int(id[0]))
                    award = Award(
                        award_type=row['award_type'].strip(),
                        current_status=row['current_award_status'].strip(),
                        start_date=datetime.strptime(row['award_start_date'], '%Y-%m-%d') if row[
                            'award_start_date'].strip() else None,
                        end_date=datetime.strptime(row['award_end_date'], '%Y-%m-%d') if row[
                            'award_end_date'].strip() else None,
                        request_date=datetime.strptime(row['award_request_date'], '%Y-%m-%d') if row[
                            'award_request_date'].strip() else None,
                        ceremony_date=datetime.strptime(row['ceremony_date'], '%Y-%m-%d') if row[
                            'ceremony_date'].strip() else None,
                        requester_full_name=row['requester_full_name'],
                        officer=officer1
                    )

                    award.save()

                print("Enabling constraints")


        logger.info("Awards Finished successfully")
