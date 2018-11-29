from django.core.management import BaseCommand

from data_importer.ipra_portal_crawler.service import AutoOpenIPRA


class Command(BaseCommand):
    def handle(self, *args, **options):
        AutoOpenIPRA.import_new()
