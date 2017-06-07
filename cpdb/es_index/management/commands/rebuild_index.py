from django.core.management import BaseCommand
from django.utils.module_loading import autodiscover_modules

from es_index import indexer_klasses, index_klasses, index_klasses_map, indexer_klasses_map


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app', nargs='*')

    def handle(self, *args, **options):
        autodiscover_modules('indexers')
        autodiscover_modules('indices')

        indices = []
        indexers = []
        if len(options['app']):
            for app in options['app']:
                indices = indices + list(index_klasses_map[app])
                indexers = indexers + list(indexer_klasses_map[app])
        else:
            indices = index_klasses
            indexers = indexer_klasses

        for index in indices:
            index.delete(ignore=404)
            index.create()
        for indexer_klass in indexers:
            indexer_klass().reindex()
