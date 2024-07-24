import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from data.models import Salary, Officer
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
                Salary.objects.all().delete()
                cursor = connection.cursor()
                cursor.execute(f"""
                                select 
                                    t.*, 
                                    cast(cast(o.officer_id as float) as int) as officer_id
                                from {table_name} t 
                                left join data_officer o 
                                    on o.uid = cast(cast(t.uid as float) as int)""")
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))

                    officer1 = Officer.objects.get(pk=row['officer_id'])
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

        logger.info("Salaries Finished successfully")
