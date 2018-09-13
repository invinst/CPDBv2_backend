import time

from django.core.management import BaseCommand
from django.db import connection

from tqdm import tqdm

from data.models import Officer
from data import officer_percentile
from utils.bulk_db import build_bulk_update_sql


class Command(BaseCommand):
    def update_percentile_to_db(percentile_values):
        if percentile_values:
            Officer.objects.all().update(
                complaint_percentile=None,
                civilian_allegation_percentile=None,
                internal_allegation_percentile=None,
                trr_percentile=None,
                honorable_mention_percentile=None,
            )

            data = [{
                'id': officer.officer_id,
                'complaint_percentile': getattr(officer, 'percentile_allegation', None),
                'civilian_allegation_percentile': getattr(officer, 'percentile_allegation_civilian', None),
                'internal_allegation_percentile': getattr(officer, 'percentile_allegation_internal', None),
                'trr_percentile': getattr(officer, 'percentile_trr', None),
                'honorable_mention_percentile': getattr(officer, 'percentile_honorable_mention', None),
            } for officer in percentile_values]

            update_fields = [
                'complaint_percentile',
                'civilian_allegation_percentile',
                'internal_allegation_percentile',
                'trr_percentile',
                'honorable_mention_percentile'
            ]

            cursor = connection.cursor()

            batch_size = 100
            for i in tqdm(range(0, len(data), batch_size)):
                batch_data = data[i:i + batch_size]
                update_command = build_bulk_update_sql(Officer._meta.db_table, 'id', update_fields, batch_data)
                cursor.execute(update_command)

    def handle(self, *args, **kwargs):
        start_time = time.time()

        # calculate all percentile and only calculate percentile_allegation
        top_percentile = officer_percentile.latest_year_percentile()
        self.update_percentile_to_db(top_percentile)

        self.stdout.write("Finished on --- %s seconds ---" % (time.time() - start_time))
