import logging
from csv import DictReader
import csv
import sys
from django.core.management import BaseCommand
from django.db import DatabaseError, transaction
from django.db import connection
from datetime import date
from tqdm import tqdm
from data.models import Officer, Allegation, Area
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

        with open(file_path) as f, open('error_complaints_complaints.csv', 'w', newline='') as error_file:
            reader = DictReader(f)

            fieldnames = reader.fieldnames
            error_writer = csv.DictWriter(error_file, fieldnames=fieldnames)
            error_writer.writeheader()

            tag = ''
            eastern = pytz.utc

            with transaction.atomic():
                with connection.constraint_checks_disabled():
                    cursor = connection.cursor()
                    #cursor.execute('ALTER TABLE data_officer DISABLE TRIGGER ALL;')
                    #print("Deleting previous objects")
                    #Officer.objects.all().delete()
                    #print("Dropping constraints")
                    #cursor.execute('ALTER TABLE public.data_officer ALTER COLUMN tags DROP NOT NULL;')
                    #cursor.execute('SET CONSTRAINTS ALL DEFERRED;')


                    for row in tqdm(reader, desc='Updating complaints(allegations)'):
                        try:
                            allegation = Allegation.objects.get(crid=row['cr_id'].replace("-", ""))
                        except Allegation.DoesNotExist:
                            allegation = Allegation(
                                                crid=row['cr_id'].replace("-", ""),
                                                created_at=date.today())

                        # street_direction
                        #state
                        #zip
                        #location_code
                        #last_filename
                        #filenames

                        allegation.first_start_date = datetime.strptime(row['complaint_date'], '%Y-%m-%d') if row[
                            'complaint_date'].strip() else None
                        allegation.first_end_date = datetime.strptime(row['closed_date'], '%Y-%m-%d') if row[
                            'closed_date'].strip() else None
                        if row['incident_date'] != '':
                            incident_value = row['incident_date'] + " " + (row['incident_time'] if row[
                                'incident_time'].strip() else '00:00:00')
                            try:
                                dt = datetime.strptime(incident_value, '%Y-%m-%d %H:%M:%S')
                                localized_dt = eastern.localize(dt)
                                allegation.incident_date = localized_dt
                            except pytz.AmbiguousTimeError as e:
                                allegation.incident_date = incident_value

                        allegation.add1 = row['add1'].strip()
                        allegation.add2 = row['add2'].strip()
                        allegation.city = row['city'].strip()
                        allegation.old_complaint_address = row['old_complaint_address'].strip()

                        try:
                            beat_id = row['beat'].replace(" ", "").split('.')
                            if beat_id[0] != '':
                                beat = Area.objects.get(id=beat_id[0])
                                allegation.beat = beat
                        except Area.DoesNotExist:
                            error_writer.writerow(row)
                            logger.error(f"Area with id {beat_id[0]} does not exist. Logged row to error file.")

                        allegation.location = row['location'].strip()
                        if (row['latitude']!='' and row['longitude']!=''):
                            allegation.point = Point(float(row['latitude']), float(row['longitude']))


                        allegation.save()


        logger.info("Finished successfully")
