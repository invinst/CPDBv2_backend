import logging
from django.core.management import BaseCommand
from django.db import transaction
from django.db import connection
from datetime import date
from data.models import Officer, Allegation, OfficerAllegation, AllegationCategory

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
            OfficerAllegation.objects.all().delete()
            with connection.constraint_checks_disabled():
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM " + table_name)
                columns = [col[0] for col in cursor.description]
                for data in cursor.fetchall():
                    row = dict(zip(columns, data))
                    # days
                    # final_penalty
                    # recc_penalty
                    if row['uid'].strip() != '':
                        id = row['uid'].split('.')
                        # print(id[0])
                        officer = Officer.objects.get(id=id[0])

                    officer_allegation = OfficerAllegation(
                        created_at=date.today(),
                        officer=officer,
                        final_finding=row['final_finding'],
                        final_outcome=row['final_outcome'],
                        recc_finding=row['recc_finding'],
                        recc_outcome=row['recc_outcome'],
                    )
                    try:
                        allegation = Allegation.objects.get(crid=row['cr_id'].replace("-", ""))
                        officer_allegation.allegation = allegation
                    except Allegation.DoesNotExist:
                        continue

                    category = None
                    try:
                        if row['complaint_code'] != '':
                            category = AllegationCategory.objects.get(category_code=row['complaint_code'])
                    except AllegationCategory.DoesNotExist:
                        last_id = AllegationCategory.objects.last().id

                        category = AllegationCategory(
                                id=last_id+1,
                                category_code=row['complaint_code'],
                                category=row['complaint_category'])
                        category.save()
                    if category is not None:
                        officer_allegation.allegation_category = category

                    officer_allegation.save()

        logger.info("Complaints Accused Finished successfully")
