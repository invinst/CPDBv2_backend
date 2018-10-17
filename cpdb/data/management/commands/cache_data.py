import time

from django.core.management import BaseCommand
from data import cache_managers


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        start_time = time.time()
        cache_managers.cache_all()
        self.stdout.write("Finished on --- %s seconds ---" % (time.time() - start_time))
