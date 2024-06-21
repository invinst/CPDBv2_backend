import logging
from csv import DictReader
# import sys
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from datetime import date
from tqdm import tqdm
from data.models import Salary, Officer
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
                    Salary.objects.all().delete()

                    for row in tqdm(reader, desc='Updating salarys'):

                        id = row['UID'].split('.')
                        officer1 = Officer.objects.get(pk=int(id[0]))
                        amount = row['salary'].split('.')
                        age = row['age_at_hire'].split('.')
                        salary = Salary(
                            pay_grade=row['pay_grade'].strip(),
                            rank=row['rank'].strip(),
                            salary=int(amount[0]),
                            employee_status=row['employee_status'].strip(),
                            org_hire_date=datetime.strptime(row['org_hire_date'], '%Y-%m-%d') if row[
                                'org_hire_date'].strip() else None,
                            spp_date=datetime.strptime(row['spp_date'], '%Y-%m-%d') if row[
                                'spp_date'].strip() else None,
                            start_date=datetime.strptime(row['start_date'], '%Y-%m-%d') if row[
                                'start_date'].strip() else None,
                            year=row['year'].strip(),
                            age_at_hire=int(age[0]) if age[0] != '' else 0,
                            officer=officer1
                        )

                        salary.save()

                    print("Enabling constraints")

        logger.info("Finished successfully")
