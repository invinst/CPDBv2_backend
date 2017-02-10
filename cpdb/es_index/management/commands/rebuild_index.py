from django.core.management import BaseCommand
from django.utils.module_loading import autodiscover_modules

from es_index import indexer_klasses, index_klasses


class Command(BaseCommand):
    def handle(self, *args, **options):
        autodiscover_modules('indexers')
        autodiscover_modules('indices')
        for index in index_klasses:
            index.delete(ignore=404)
            index.create()
        for indexer_klass in indexer_klasses:
            indexer_klass().reindex()
