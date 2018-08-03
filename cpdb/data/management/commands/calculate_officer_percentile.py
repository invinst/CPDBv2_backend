import time

from django.core.management import BaseCommand

from tqdm import tqdm

from data.models import Officer
from data import officer_percentile


class Command(BaseCommand):
    def update_percentile_to_db(self, percentile_values):
        if percentile_values:
            Officer.objects.all().update(
                complaint_percentile=None,
                civilian_allegation_percentile=None,
                internal_allegation_percentile=None,
                trr_percentile=None,
                honorable_mention_percentile=None,
            )
            for data in tqdm(percentile_values):
                officer = Officer.objects.get(pk=data.officer_id)
                if officer:
                    if hasattr(data, 'percentile_allegation'):
                        officer.complaint_percentile = data.percentile_allegation
                    if hasattr(data, 'percentile_allegation_civilian'):
                        officer.civilian_allegation_percentile = data.percentile_allegation_civilian
                    if hasattr(data, 'percentile_allegation_internal'):
                        officer.internal_allegation_percentile = data.percentile_allegation_internal
                    if hasattr(data, 'percentile_trr'):
                        officer.trr_percentile = data.percentile_trr
                    if hasattr(data, 'percentile_honorable_mention'):
                        officer.honorable_mention_percentile = data.percentile_honorable_mention
                    officer.save()

    def handle(self, *args, **kwargs):
        start_time = time.time()

        # calculate all percentile and only calculate percentile_allegation
        top_percentile = officer_percentile.latest_year_percentile()
        self.update_percentile_to_db(top_percentile)

        self.stdout.write("Finished on --- %s seconds ---" % (time.time() - start_time))
