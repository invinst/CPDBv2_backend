import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from datetime import date
from data.models import Allegation, Complainant

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
                Complainant.objects.all().delete()

                cursor = connection.cursor()
                cursor.execute("SELECT * FROM " + table_name)
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))

                    complaint = Complainant(
                        created_at=date.today(),
                        race=row['race'],
                    )
                    if row['age'] != '':
                        age = row['age']
                        complaint.age = age
                    if row['birth_year'] != '':
                        year = row['birth_year']
                        complaint.birth_year = year
                    if row['gender'] != '':
                        complaint.gender = row['gender'][0]

                    try:
                        allegation = Allegation.objects.get(crid=row['cr_id'].replace("-", ""))
                        complaint.allegation = allegation
                    except Allegation.DoesNotExist:
                        continue

                    # print(row)
                    complaint.save()

        logger.info("Complaints Finished successfully")
