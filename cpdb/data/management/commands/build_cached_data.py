import time

from django.core.management import BaseCommand
from data.cache_managers import allegation_cache_manager, officer_cache_manager


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        start_time = time.time()
        allegation_cache_manager.cache_data()
        officer_cache_manager.cache_data()
        self.stdout.write("Finished on --- %s seconds ---" % (time.time() - start_time))
