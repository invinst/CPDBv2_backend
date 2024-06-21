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
        parser.add_argument('--file_path', help='Path to the CSV file')


    def handle(self, *args, **kwargs):
        file_path = kwargs.get('file_path')

        if not file_path:
            logger.error("Please provide a valid file path.")
            return

        with open(file_path) as f:
            reader = DictReader(f)

            with transaction.atomic():
                with connection.constraint_checks_disabled():
                    # cursor = connection.cursor()
                    # cursor.execute('ALTER TABLE data_salary DISABLE TRIGGER ALL;')
                    print("Deleting previous objects")
                    Award.objects.all().delete()
                    # print("Dropping constraints")
                    # cursor.execute('ALTER TABLE public.data_salary ALTER COLUMN tags DROP NOT NULL;')
                    # cursor.execute('SET CONSTRAINTS ALL DEFERRED;')

                    for row in tqdm(reader, desc='Updating salarys'):

                        id = row['UID'].split('.')
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

                        # print(row)
                        award.save()

                    # cursor.execute('ALTER TABLE data_salary ENABLE TRIGGER ALL;')
                    # cursor.execute('SET CONSTRAINTS ALL IMMEDIATE;')
                    print("Enabling constraints")
                    # cursor.execute("UPDATE public.data_salary SET tags = '{}' WHERE tags is null;")
                    # cursor.execute('ALTER TABLE public.data_salary ALTER COLUMN tags SET NOT NULL;')

        logger.info("Awards Finished successfully")
