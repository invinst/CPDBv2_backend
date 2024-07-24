import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from data.models import OfficerHistory, Officer, PoliceUnit
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
                OfficerHistory.objects.all().delete()
                cursor = connection.cursor()
                cursor.execute(f"""
                               select
                                    t.*,
                                    cast(cast(o.officer_id as float) as int) as officer_id
                                from {table_name} t
                                left join csv_officer o
                                    on o.uid = cast(cast(t.uid as float) as int)""")
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))
                    officer1 = Officer.objects.get(pk=row['officer_id'])

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

        logger.info("Unit data Finished successfully")
