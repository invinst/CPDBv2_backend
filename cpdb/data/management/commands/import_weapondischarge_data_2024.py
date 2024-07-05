import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from trr.models import TRR, WeaponDischarge

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
                            reloaded = None
                            if row['firearm_reloaded'].upper() == 'YES':
                                reloaded = True
                            if row['firearm_reloaded'].upper() == 'NO':
                                reloaded = False

                            total_shots = None
                            if row['total_number_of_shots'] != '':
                                if row['total_number_of_shots'].upper() == 'YES':
                                    total_shots = 1
                                else:
                                    if row['total_number_of_shots'].upper() != 'NO':
                                        total_shots = row['total_number_of_shots']

                            weapon = WeaponDischarge(
                                trr=trr,
                                weapon_type=row['weapon_type'],
                                weapon_type_description=row['weapon_type_description'],
                                firearm_make=row['firearm_make'],
                                firearm_model=row['firearm_model'],
                                firearm_barrel_length=row['firearm_barrel_length'],
                                firearm_caliber=row['firearm_caliber'],
                                total_number_of_shots=total_shots,
                                firearm_reloaded=reloaded,
                                handgun_worn_type=row['handgun_worn_type'],
                                handgun_drawn_type=row['handgun_drawn_type'],
                                method_used_to_reload=row['method_used_to_reload'],
                                sight_used=True if (
                                        row['sight_used'] == 'Y' or row['sight_used'] == 'Yes') else None,
                                protective_cover_used=row['protective_cover_used'],
                                discharge_distance=row['discharge_distance'],
                                object_struck_of_discharge=row['object_struck_of_discharge'],
                                discharge_position=row['discharge_position'],
                            )

                            weapon.save()
                        except TRR.DoesNotExist:
                            continue

        logger.info("Finished successfully")
