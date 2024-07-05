import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from trr.models import TRR, SubjectWeapon

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
                cursor.execute("SELECT * FROM " + table_name)
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))
                    if row['trr_id'] != '':
                        try:
                            trr = TRR.objects.get(pk=row['trr_id'].replace("-", ""))

                            weapon = SubjectWeapon(
                                trr=trr,
                                weapon_type=row['weapon_type'],
                                firearm_caliber=row['firearm_caliber'],
                                weapon_description=row['weapon_description'] if
                                len(row['weapon_description']) < 150 else None,
                            )

                            weapon.save()
                        except TRR.DoesNotExist:
                            continue

        logger.info("TRR Subject Weapon Finished successfully")
