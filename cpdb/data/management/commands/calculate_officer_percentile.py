import time

from django.core.management import BaseCommand

from data.models import Officer


class Command(BaseCommand):
    def update_percentile_to_db(self, percentile_values):
        if percentile_values:
            Officer.objects.all().update(complaint_percentile=None)
            for data in percentile_values:
                officer = Officer.objects.get(pk=data.officer_id)
                if officer:
                    officer.complaint_percentile = data.percentile_allegation
                    officer.save()

    def handle(self, *args, **kwargs):
        start_time = time.time()

        # calculate all percentile and only calculate percentile_allegation
        top_percentile = Officer.top_allegation_percentile()
        self.update_percentile_to_db(top_percentile)

        self.stdout.write("Finished on --- %s seconds ---" % (time.time() - start_time))
