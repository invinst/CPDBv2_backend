import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from trr.models import TRR, TRRStatus
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--table_name', help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        table_name = kwargs.get('table_name')

        if not table_name:
            logger.error("Please provide a valid file path.")
            return

        eastern = pytz.utc

        with transaction.atomic():
            with connection.constraint_checks_disabled():
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM " + table_name)
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))
                    if row['trr_id'] != '':
                        try:
                            trr = TRR.objects.get(pk=row['trr_id'].replace("-", ""))
                            status = TRRStatus(
                                trr=trr,
                                # officer=officer,
                                rank=row['rank'],
                                star=row['star'],
                                status=row['status'],
                                age=row['age'],
                            )
                            try:
                                dt = datetime.strptime(row['status_date'] + " " + row['status_time'],
                                                       '%Y-%m-%d %H:%M:%S')
                                localized_dt = eastern.localize(dt)
                                status.status_datetime = localized_dt
                            except pytz.AmbiguousTimeError:
                                print("Except")
                                # trr.incident_date = incident_value

                            status.save()
                        except TRR.DoesNotExist:
                            continue

        logger.info("TRR Statuses Finished successfully")
