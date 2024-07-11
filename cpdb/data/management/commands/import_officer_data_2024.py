import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from data.models import Officer, OfficerBadgeNumber
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
        try:
            tag = ''
            with transaction.atomic():
                with connection.constraint_checks_disabled():
                    cursor = connection.cursor()

                    print("Dropping constraints")
                    cursor.execute('SET CONSTRAINTS ALL IMMEDIATE;')
                    cursor.execute('ALTER TABLE public.data_officer ALTER COLUMN tags DROP NOT NULL;')
                    print("Deleting previous objects")
                    cursor.execute('delete from trr_charge where trr_id in (select id from trr_trr where officer_id in (select id from data_officer) )')
                    cursor.execute('delete from trr_subjectweapon where trr_id in (select id from trr_trr where officer_id in (select id from data_officer) )')
                    cursor.execute('delete from trr_actionresponse where trr_id in (select id from trr_trr where officer_id in (select id from data_officer) )')
                    cursor.execute('delete from trr_trrattachmentrequest where trr_id in (select id from trr_trr where officer_id in (select id from data_officer) )')
                    cursor.execute('delete from trr_trrstatus where trr_id in (select id from trr_trr where officer_id in (select id from data_officer) )')
                    cursor.execute('delete from trr_weapondischarge where trr_id in (select id from trr_trr where officer_id in (select id from data_officer) )')
                    cursor.execute('delete from pinboard_pinboard_trrs  where trr_id in (select id from trr_trr where officer_id in (select id from data_officer) )')
                    cursor.execute('delete from trr_trr where officer_id in (select id from data_officer)')
                    print("Deleting officers")
                    Officer.objects.all().delete()

                    cursor.execute("SELECT * FROM " + table_name)
                    columns = [col[0] for col in cursor.description]
                    for data in cursor.fetchall():
                        row = dict(zip(columns, data))

                        officer = Officer(id=row['uid'])
                        officer.last_name = row['last_name'].strip()
                        officer.first_name = row['first_name'].strip()
                        officer.middle_initial = row['middle_initial'].strip()
                        officer.middle_initial2 = row['middle_initial2'].strip()
                        officer.suffix_name = row['suffix_name'].strip()
                        if row['birth_year'] is None:
                            officer.birth_year = None
                        else:
                            officer.birth_year = row['birth_year']
                        officer.race = row['race'].strip()
                        officer.gender = row['gender'].strip()[0] if row['gender'].strip() else ''
                        officer.appointed_date = datetime.strptime(row['appointed_date'], '%Y-%m-%d') if row[
                            'appointed_date'].strip() else None
                        officer.resignation_date = datetime.strptime(row['resignation_date'], '%Y-%m-%d') if row[
                            'resignation_date'].strip() else None
                        officer.current_status = row['current_status']
                        officer.current_star = row['current_star']
                        officer.current_unit = row['current_unit']
                        officer.current_rank = row['current_rank'].strip()
                        officer.foia_names = row['foia_names'].strip()
                        officer.matches = row['matches'].strip()
                        officer.profile_count = row['profile_count']

                        if not tag:
                            tag = officer.tags
                            logger.info(f"Tag set to: {tag}")

                        officer.save()

                        if officer.current_star is not None:
                            badge = OfficerBadgeNumber(
                                officer=officer,
                                star=officer.current_star,
                                current=officer.current_status
                            )
                            badge.save()

                    cursor.execute("UPDATE public.data_officer SET tags = '{}' WHERE tags is null;")
                    cursor.execute('ALTER TABLE public.data_officer ALTER COLUMN tags SET NOT NULL;')
                    cursor.execute('SET CONSTRAINTS ALL DEFERRED;')
        except Exception as ex:
            print(ex)

        logger.info("Officers Finished successfully")
