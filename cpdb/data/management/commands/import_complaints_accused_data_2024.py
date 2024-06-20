import logging
from csv import DictReader
import csv
from django.core.management import BaseCommand
from django.db import DatabaseError, transaction
from django.db import connection
from datetime import date
from tqdm import tqdm
from data.models import Officer, Allegation, OfficerAllegation, AllegationCategory
from datetime import datetime
from django.contrib.gis.geos import Point
import pytz

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file_path', help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs.get('file_path')

        if not file_path:
            logger.error("Please provide a valid file path.")
            return

        with open(file_path) as f, open('error_complaints_accused.csv', 'w', newline='') as error_file:
            reader = DictReader(f)

            fieldnames = reader.fieldnames
            error_writer = csv.DictWriter(error_file, fieldnames=fieldnames)
            error_writer.writeheader()
            tag = ''
            eastern = pytz.utc

            with transaction.atomic():
                OfficerAllegation.objects.all().delete()
                with connection.constraint_checks_disabled():
                    cursor = connection.cursor()

                    for row in tqdm(reader, desc='Updating officer allegations'):

                        #days
                        #final_penalty
                        #recc_penalty
                        if row['UID'].strip() != '':
                            id = row['UID'].split('.')
                            #print(id[0])
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
                            error_writer.writerow(row)
                            print("Not found")
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
