import logging
from csv import DictReader
import csv
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from datetime import date
from tqdm import tqdm
from data.models import Allegation, Victim
# from datetime import datetime
# from django.contrib.gis.geos import Point
# import pytz

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
                cursor = connection.cursor()
                cursor.execute('SET CONSTRAINTS ALL IMMEDIATE;')
                cursor.execute('ALTER TABLE public.data_victim ALTER COLUMN allegation_id DROP NOT NULL;')
                Victim.objects.all().delete()
                cursor.execute("SELECT * FROM " + table_name)
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))

                    victim = Victim(
                        created_at=date.today(),
                        gender=row['gender'].strip()[0] if row['gender'].strip() != '' else '',
                        race=row['race'],
                        age=row['age'],
                        birth_year=row['birth_year']
                    )

                    try:
                        allegation = Allegation.objects.get(crid=row['cr_id'].replace("-", ""))
                        victim.allegation = allegation
                    except Allegation.DoesNotExist:
                        continue

                    victim.save()

                cursor.execute('ALTER TABLE public.data_victim ALTER COLUMN allegation_id SET NOT NULL;')
                cursor.execute('SET session_replication_role = default;')
                cursor.execute('SET CONSTRAINTS ALL DEFERRED;')

        logger.info("Victims Finished successfully")
