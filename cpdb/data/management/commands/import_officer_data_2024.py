import logging
from csv import DictReader
# import sys
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
# from datetime import date
from tqdm import tqdm
from data.models import Officer
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
            tag = ''
            with transaction.atomic():
                with connection.constraint_checks_disabled():
                    cursor = connection.cursor()
                    print("Dropping constraints")
                    cursor.execute('SET CONSTRAINTS ALL IMMEDIATE;')
                    cursor.execute('ALTER TABLE public.data_officer ALTER COLUMN tags DROP NOT NULL;')
                    print("Deleting previous objects")
                    cursor.execute('delete from trr_trr where officer_id in (select id from data_officer);')
                    Officer.objects.all().delete()

                    for row in tqdm(reader, desc='Updating officers'):
                        officer = Officer(id=row['UID'])

                        officer.last_name = row['last_name'].strip()
                        officer.first_name = row['first_name'].strip()
                        officer.middle_initial = row['middle_initial'].strip()
                        officer.middle_initial2 = row['middle_initial2'].strip()
                        officer.suffix_name = row['suffix_name'].strip()
                        if row['birth_year'].strip() == '':
                            officer.birth_year = None
                        else:
                            officer.birth_year = row['birth_year'].strip()
                        officer.race = row['race'].strip()
                        officer.gender = row['gender'].strip()[0] if row['gender'].strip() else ''
                        officer.appointed_date = datetime.strptime(row['appointed_date'], '%Y-%m-%d') if row[
                            'appointed_date'].strip() else None
                        officer.resignation_date = datetime.strptime(row['resignation_date'], '%Y-%m-%d') if row[
                            'resignation_date'].strip() else None
                        officer.current_status = row['current_status'].strip()
                        officer.current_star = row['current_star'].strip()
                        officer.current_unit = row['current_unit'].strip()
                        officer.current_rank = row['current_rank'].strip()
                        officer.foia_names = row['foia_names'].strip()
                        officer.matches = row['matches'].strip()
                        officer.profile_count = row['profile_count'].strip()

                        if not tag:
                            tag = officer.tags
                            logger.info(f"Tag set to: {tag}")

                        officer.save()

                    cursor.execute("UPDATE public.data_officer SET tags = '{}' WHERE tags is null;")
                    cursor.execute('ALTER TABLE public.data_officer ALTER COLUMN tags SET NOT NULL;')
                    cursor.execute('SET CONSTRAINTS ALL DEFERRED;')

        logger.info("Officers Finished successfully")
