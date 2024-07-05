import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from trr.models import TRR, ActionResponse

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
                            action_response = ActionResponse(
                                person=row['person'],
                                resistance_type=row['resistance_type'],
                                action=row['action'],
                                other_description=row['other_description'],
                                member_action=row['member_action'],
                                force_type=row['force_type'],
                                action_sub_category=row['action_sub_category'],
                                action_category=row['action_category'].split('.')[0] if
                                row['action_category'] != '' else None,
                                resistance_level=row['resistance_level']
                            )
                            action_response.trr = trr
                            action_response.save()

                        except TRR.DoesNotExist:
                            continue

        logger.info("TRR Action Response Finished successfully")
