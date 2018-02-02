import time

from django.core.management import BaseCommand

from data.models import Officer


class Command(BaseCommand):
    def update_percentile_to_db(self, percentile_values):
        if percentile_values:
            Officer.objects.all().update(complaint_percentile=None)
            for officer_id, score in percentile_values:
                officer = Officer.objects.get(pk=officer_id)
                if officer:
                    officer.complaint_percentile = score
                    officer.save()

    def handle(self, *args, **kwargs):
        start_time = time.time()

        top_percentile = Officer.top_complaint_officers(100)  # calculate all
        self.update_percentile_to_db(top_percentile)

        self.stdout.write("Finished on --- %s seconds ---" % (time.time() - start_time))
