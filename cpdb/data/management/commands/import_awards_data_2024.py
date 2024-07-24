import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
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

                print("Done deleting previous objects")
                cursor = connection.cursor()
                cursor.execute(f"""
                               select
                                    t.*,
                                    cast(cast(o.officer_id as float) as int) as officer_id
<<<<<<< HEAD
                                from {table_name} t
                                left join data_officer o
=======
                                from {table_name} t 
                                left join csv_officer o 
>>>>>>> 2b0ddf5a (should be 'csv_officer' not 'data_offficer'. fixed)
                                    on o.uid = cast(cast(t.uid as float) as int)""")
                columns = [col[0] for col in cursor.description]
                x = 1
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))
                    officer1 = Officer.objects.get(pk=row['officer_id'])
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
                    print("award " + x + " done")
                    x = x + 1

                print("Enabling constraints")

        logger.info("Awards Finished successfully")
