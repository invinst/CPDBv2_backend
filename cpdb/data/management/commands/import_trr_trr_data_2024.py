import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from datetime import date
from data.models import Officer, PoliceUnit
from trr.models import TRR
from datetime import datetime
from django.contrib.gis.geos import Point
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
                cursor.execute('ALTER TABLE public.data_policeunit ALTER COLUMN tags DROP NOT NULL;')
                cursor.execute("SELECT * FROM " + table_name)
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))
                    if row['uid'] != '':
                        officer_id = row['uid'].split('.')
                        officer = Officer.objects.get(pk=int(officer_id[0]))

                    try:
                        total_shots = float(row['total_number_of_shots'])
                    except ValueError:
                        total_shots = 0
                    trr = TRR(
                        id=row['trr_id'].replace("-", ""),
                        direction=row['direction'],
                        street=row['street'],
                        location=row['location'],
                        indoor_or_outdoor=row['indoor_or_outdoor'],
                        lighting_condition=row['lighting_condition'],
                        weather_condition=row['weather_condition'],
                        notify_OEMC=True if (row['notify_oemc'] == 'Y' or row['notify_oemc'] == 'Yes') else False,
                        notify_district_sergeant=True if (row['notify_district_sergeant'] == 'Y' or row['notify_district_sergeant'] == 'Yes') else False,
                        notify_OP_command=True if (row['notify_op_command'] == 'Y' or row['notify_op_command'] == 'Yes') else False,
                        notify_DET_division=True if (row['notify_det_division'] == 'Y' or row['notify_det_division'] == 'Yes') else False,
                        number_of_weapons_discharged=float(row['number_of_weapons_discharged']) if row['number_of_weapons_discharged'] != '' else 0,
                        party_fired_first=row['party_fired_first'],
                        location_recode=row['location_recode'],
                        taser=row['taser'],
                        total_number_of_shots=total_shots,
                        firearm_used=row['firearm_used'],
                        number_of_officers_using_firearm=float(row['number_of_officers_using_firearm']) if row['number_of_officers_using_firearm'] != '' else 0,
                        officer_assigned_beat=row['officer_assigned_beat'],
                        officer_on_duty=True if row['officer_on_duty'] == '1' else False,
                        officer_in_uniform=True if row['officer_in_uniform'] == '1' else False,
                        officer_injured=True if row['officer_injured'] == '1' else False,
                        officer_rank=row['officer_rank'],
                        subject_id=float(row['subject_id']) if row['subject_id'] != '' else None,
                        subject_armed=True if (row['subject_armed'] == 'Y' or row['subject_armed'] == 'Yes') else False,
                        subject_injured=True if (row['subject_injured'] == 'Y' or row['subject_injured'] == 'Yes') else False,
                        subject_alleged_injury=True if (row['subject_alleged_injury'] == 'Y' or row['subject_alleged_injury'] == 'Yes') else False,
                        subject_age=row['subject_age'] if row['subject_age'] != '' else None,
                        subject_birth_year=float(row['subject_birth_year']) if row['subject_birth_year'] != '' else None,
                        subject_gender=row['subject_gender'][0] if row['subject_gender'] != '' else None,
                        subject_race=row['subject_race'],
                        created_at=date.today()
                    )
                    try:
                        dt = datetime.strptime(row['trr_datetime'], '%Y-%m-%d %H:%M:%S')
                        localized_dt = eastern.localize(dt)
                        trr.trr_datetime = localized_dt
                    except pytz.AmbiguousTimeError:
                        print("Except")
                    except ValueError:
                        dt = datetime.strptime(row['trr_datetime'], '%Y-%m-%d')
                        localized_dt = eastern.localize(dt)
                        trr.trr_datetime = localized_dt

                        # trr.incident_date = incident_value

                    if (row['latitude'] != '' and row['longitude'] != ''):
                        trr.point = Point(float(row['longitude']), float(row['latitude']))
                    if row['uid'] != '':
                        trr.officer = officer
                    if row['beat'] != '':
                        trr.beat = row['beat'].split('.')[0]

                    if row['officer_unit_id'] != '':
                        try:
                            policy_unit = PoliceUnit.objects.get(id=float(row['officer_unit_id']))
                        except PoliceUnit.DoesNotExist:
                            name = row['officer_unit_detail_id'] if row['officer_unit_detail_id'] != '' else str(row['officer_unit_id'])
                            policy_unit = PoliceUnit(id=float(row['officer_unit_id']), unit_name=name, tags='{}')
                            policy_unit.save()
                        trr.officer_unit_id = policy_unit.id

                    trr.save()
                cursor.execute("UPDATE public.data_policeunit SET tags = '{}' WHERE tags is null;")
                cursor.execute('ALTER TABLE public.data_policeunit ALTER COLUMN tags SET NOT NULL;')

        logger.info("Finished successfully")
