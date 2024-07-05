import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from data.models import Allegation, Investigator, InvestigatorAllegation, PoliceUnit
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
            Investigator.objects.all().delete()
            with connection.constraint_checks_disabled():
                # cursor = connection.cursor()
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM " + table_name)
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))
                    investigator = Investigator(
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        middle_initial=row['middle_initial'],
                        suffix_name=row['suffix_name'],
                        appointed_date=datetime.strptime(row['appointed_date'], '%Y-%m-%d') if row[
                            'appointed_date'].strip() else None
                    )
                    investigator.save()

                    investigator_allegation = InvestigatorAllegation(
                        investigator=investigator,
                        current_star=row['current_star'],
                        current_rank=row['current_rank'],

                    )
                    if row['current_unit'] != '':
                        unit = row['current_unit']
                        policy_unit = PoliceUnit.objects.filter(
                            unit_name=str(unit).zfill(3)
                        )
                        if len(policy_unit) > 0:
                            investigator_allegation.current_unit = policy_unit[0]

                    try:
                        allegation = Allegation.objects.get(crid=row['cr_id'].replace("-", ""))
                        investigator_allegation.allegation = allegation
                    except Allegation.DoesNotExist:
                        continue

                    investigator_allegation.save()

        logger.info("Investigators Finished successfully")
