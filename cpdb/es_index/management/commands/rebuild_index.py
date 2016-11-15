from django.core.management import BaseCommand

from es_index.autodiscover import autodiscover_module
from es_index import indexers


class Command(BaseCommand):
    def handle(self, *args, **options):
        autodiscover_module('indexers')
        for indexer_klass in indexers:
            indexer_klass().reindex()
